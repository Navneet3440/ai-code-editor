from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    status
)
from sqlalchemy.orm import Session

from app.auth_helper import get_current_user
from app.database import get_db
from app.editor.editor_schema import DebuggerRequest, CodeGeneratorRequest
from app.editor.editor_service import analyze_debugger, generate_code, session_websocket

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def session_websocket_router(
    websocket: WebSocket,
    session_id: str
):
    await session_websocket(websocket, session_id)

@router.post("/debugger")
async def debugger_endpoint(
    request: DebuggerRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await analyze_debugger(request.code, request.language)
    return {"analysis": result}

@router.post("/generate")
async def code_generator_endpoint(
    request: CodeGeneratorRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    code = await generate_code(request.prompt, request.language)
    return {"generated_code": code}