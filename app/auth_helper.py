import jwt
from datetime import datetime, timedelta, timezone
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
from app.user.user_crud import get_user_by_user_id
from app.user.user_model import User
from app.app_config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def generate_jwt_token(data: dict, expires_delta: timedelta = None):
    """Generate a JWT token with the provided data and expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str):
    """Verify and decode a JWT token. Return None if the token is invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_jwt_token(token)
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

    payload = verify_jwt_token(session_token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect("Invalid token")

    user_id: str = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise WebSocketDisconnect("Invalid token payload")

    return user_id
