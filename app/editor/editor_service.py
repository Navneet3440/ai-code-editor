import json
import re
import redis.asyncio as redis
from openai import AsyncOpenAI
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.database import SessionLocal
from app.auth_helper import ws_get_user
from app.app_config import OPENAI_API_KEY, OPENAI_API_MODEL, REDIS_HOST, REDIS_PORT, REDIS_DB
from app.session.session_crud import check_user_session_access, get_session_by_id
from app.utils.logging_config import logger

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)



def extract_code(content: str) -> list:
    pattern = r"```.*?\n(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return content

class ConnectionManager:
    def __init__(self):
        self.active_sessions: Dict[str, List[WebSocket]] = {}
        self.redis = redis_client

    async def connect(self, session_id: str, websocket: WebSocket):
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(websocket)
        await self.redis.incr(f"session:{session_id}:connections")

    async def disconnect(self, session_id: str, websocket: WebSocket):
        content = None
        if session_id in self.active_sessions:
            content = await self.get_content(session_id)
            self.active_sessions[session_id].remove(websocket)
            count = await self.redis.decr(f"session:{session_id}:connections")
            if count <= 0:
                await self.redis.delete(f"session:{session_id}:connections")
                await self.redis.delete(f"session:{session_id}:content")
            if not self.active_sessions[session_id]:
                del self.active_sessions[session_id]
        
        return content

    async def broadcast(self, session_id: str, message: str, type: str = "update"):
        await self.redis.set(f"session:{session_id}:content", message)
        broadcast_message = {
            "type": type,
            "content": message
        }
        for connection in self.active_sessions.get(session_id, []):
            await connection.send_json(broadcast_message)


    async def get_content(self, session_id: str) -> str:
        content = await self.redis.get(f"session:{session_id}:content")
        if content is None:
            return ""
        return content.decode("utf-8")

manager = ConnectionManager()


async def websocket_session(
    websocket: WebSocket,
    session_id: str
    ):
    db_connection = SessionLocal()
    try:
        await websocket.accept()
        
        user_id = await ws_get_user(websocket)
        valid_user = check_user_session_access(db_connection, user_id, session_id)
        if not valid_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning(f"Unauthorized access attempt by user -{user_id}")
            return
        logger.debug(f"User has access to the session")
    
        session_obj = get_session_by_id(db_connection, session_id)
        if not session_obj:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.error(f"Missing session {session_id}")
            return
        logger.debug(f"Session is a valid session")
        
        try:
            initial_content = await manager.get_content(session_id)
            if not initial_content:
                initial_content = session_obj.content or ""
                await manager.redis.set(f"session:{session_id}:content", initial_content)
        except RedisError as e:
            logger.error(f"Redis init failed: {e}")
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            return
            
        content = {"type": "update", "content": initial_content}
        await websocket.send_json(content)
        await manager.connect(session_id, websocket)

        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            await manager.broadcast(session_id, data["content"])

    except WebSocketDisconnect:
        content = await manager.disconnect(session_id, websocket)
        if content:
            session_obj.content = content
            db_connection.commit()
    except Exception as e:
        logger.error(e,exc_info=True)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        db_connection.close()



async def get_code_content(session_id: str, db: Session) -> str:
    code = await manager.get_content(session_id)
    if not code:
        code_session = get_session_by_id(db, session_id)
        if not code_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        code = code_session.content or ""
        await manager.redis.set(f"session:{session_id}:content", code)
    return code


async def debug_code(db: Session, session_id: str) -> str:
    code = await get_code_content(session_id, db)
    
    system_prompt = (
        "You are an expert code analyst with deep knowledge of programming languages and debugging techniques. "
        "Analyze the provided code to identify the following:\n"
        "1. Syntax errors and their exact locations.\n"
        "2. Logical errors and potential bugs.\n"
        "3. Performance bottlenecks and optimization opportunities.\n"
        "4. Security vulnerabilities and best practices.\n"
        "5. Code style improvements (e.g., PEP 8 for Python).\n\n"
        "Format your response as a structured markdown list with clear headings for each category. "
        "Provide actionable suggestions and, where applicable, include corrected code snippets."
    )
    user_message = f"Please analyze the following code and provide debugging suggestions:\n\n```\n{code}\n```"

    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_API_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
    except Exception as e:
        logger.error(f"Debugging AI error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service error"
        )

    suggestions = response.choices[0].message.content
    return suggestions


async def generate_code_from_session(session_id: str, query: str, db: Session):
    code = await get_code_content(session_id, db)
    
    # Broadcast a lock message to disable editing during code generation
    await manager.broadcast(
        session_id=session_id,
        message="Code generation in progress. Editing is disabled.",
        type="lock"
    )
    
    system_prompt = (
        "You are an expert code generator with deep knowledge of programming languages and software development best practices. "
        "Based on the provided code and any additional instructions, generate a complete, self-contained, working code file. "
        "Your output must consist solely of the code with no extra commentary. If modifications are requested, produce the entire revised code. "
        "Ensure the generated code is:\n"
        "1. Correct and free of syntax errors.\n"
        "2. Efficient and optimized for performance.\n"
        "3. Secure and follows best practices.\n"
        "4. Well-structured and readable (e.g., PEP 8 for Python).\n"
    )
    user_message = f"Code:\n```\n{code}\n```\n\nInstructions: {query}" if query else f"Code:\n```\n{code}\n```\n\nPlease generate the complete, working code file."
    
    try:
        response = await openai_client.chat.completions.create(
            model=OPENAI_API_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
    except Exception as e:
        logger.error(f"Code generation AI error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service error"
        )

    generated_code = response.choices[0].message.content
    extracted_code = extract_code(generated_code)
    await manager.broadcast(session_id, extracted_code, type="unlock")
    return extracted_code
    