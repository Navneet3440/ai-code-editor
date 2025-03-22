from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserCreateResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True