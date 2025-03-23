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
from app.editor.editor_service import debug_code, generate_code_from_session, websocket_session

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def websocket_session_router(
    websocket: WebSocket,
    session_id: str
):
    await websocket_session(websocket, session_id)

@router.post("/ai-debugger")
async def debugger_endpoint(
    request: DebuggerRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    suggestions = await debug_code(db ,request.code_session_id)
    return {"suggestions": suggestions}


@router.post("/ai-generator")
async def code_generator_endpoint(
    request: CodeGeneratorRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    await generate_code_from_session(request.code_session_id, request.query, db)