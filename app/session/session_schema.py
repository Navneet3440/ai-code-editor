from typing import Literal, Optional
from pydantic import BaseModel
from enum import Enum as PyEnum

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


class SessionWithMembership(BaseModel):
    id: int
    session_id: str
    name: str
    content_type: str
    content: Optional[str] = None
    created_by: str
    updated_by: Optional[str] = None


class RoleEnum(PyEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"