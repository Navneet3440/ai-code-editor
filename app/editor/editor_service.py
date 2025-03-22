import json
from typing import Dict, List, Optional

import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from openai import AsyncOpenAI
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.auth_dependency import get_current_user_ws
from app.database import SessionLocal
from app.session.session_crud import get_session_by_id, check_user_session_access
from app.app_config import (
    OPENAI_API_KEY,
    OPENAI_API_MODEL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB
)

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, message: str, session_id: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_text(message)

manager = ConnectionManager()

async def session_websocket(websocket: WebSocket, session_id: str):
    try:
        user_id = await get_current_user_ws(websocket)
        async with SessionLocal() as db:
            if not await check_user_session_access(db, user_id, session_id):
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

        await manager.connect(websocket, session_id)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.broadcast(data, session_id)
        except WebSocketDisconnect:
            await manager.disconnect(websocket, session_id)
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_debugger(code: str, language: str) -> str:
    try:
        prompt = f"Analyze this {language} code for potential bugs and improvements:\n\n{code}"
        response = await openai_client.chat.completions.create(
            model=OPENAI_API_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")

async def generate_code(prompt: str, language: str) -> str:
    try:
        full_prompt = f"Generate {language} code for the following request:\n\n{prompt}"
        response = await openai_client.chat.completions.create(
            model=OPENAI_API_MODEL,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")