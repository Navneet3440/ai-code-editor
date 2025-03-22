from typing import Literal, Optional
from pydantic import BaseModel

# Session schema
class SessionCreate(BaseModel):
    name: str
    content_type: Literal["python", "javascript"]
    content: Optional[str] = None
    created_by: Optional[str] = None

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    content_type: Optional[Literal["python", "javascript"]] = None
    content: Optional[str] = None
    updated_by: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    name: str
    content_type: str
    content: Optional[str] = None
    created_by: str
    updated_by: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    is_deleted: bool = False

    class Config:
        from_attributes = True

# Session Membership schema
class SessionMembershipInvite(BaseModel):
    user_id: str
    session_id: str
    role: Literal["owner", "editor", "viewer"]

class SessionMembershipUpdate(BaseModel):
    user_id: str
    session_id: str
    role: Literal["owner", "editor", "viewer"]

class SessionMembershipResponse(BaseModel):
    id: int
    user_id: str
    session_id: str
    role: str
    created_at: str
    updated_at: Optional[str] = None
    is_deleted: bool = False

    class Config:
        from_attributes = True

class SessionWithMembership(BaseModel):
    id: int
    session_id: str
    name: str
    content_type: str
    content: Optional[str] = None
    created_by: str
    updated_by: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None
    is_deleted: bool = False
    role: str

    class Config:
        from_attributes = True
