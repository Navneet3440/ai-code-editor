from fastapi import (
    Cookie,
    Depends,
    HTTPException,
    WebSocket,
    status
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.user_auth import decode_access_token
from app.user.user_crud import get_user_by_user_id
from app.user.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = get_user_by_user_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_user_ws(websocket: WebSocket) -> str:
    cookies = websocket.cookies
    session_token = cookies.get("jwt_token")

    if not session_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect("Missing authentication cookie")

    payload = decode_access_token(session_token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect("Invalid token")

    user_id: str = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect("Invalid token payload")

    return user_id
