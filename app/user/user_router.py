from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_dependency import get_current_user, User
from app.database import get_db
from app.user.user_auth import create_access_token
from app.user.user_schema import (
    UserCreateRequest,
    UserLoginRequest,
    UserCreateResponse,
    UserListResponse
)
from app.user.user_service import (
    register_user,
    login_user,
    get_all_users_service
)

router = APIRouter()

@router.post("/register", response_model=UserCreateResponse)
async def register(request: UserCreateRequest, db: Session = Depends(get_db)):
    user = await register_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to register user"
        )
    return user

@router.post("/login")
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = await login_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token({"sub": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/list", response_model=list[UserListResponse])
async def get_all_users_router(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_all_users_service(db)