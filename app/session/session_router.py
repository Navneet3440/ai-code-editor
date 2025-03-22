from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_dependency import get_current_user, User
from app.database import get_db
from app.session.session_schema import (
    SessionCreate,
    SessionUpdate,
    SessionMembershipInvite,
    SessionMembershipUpdate,
    SessionResponse,
    SessionMembershipResponse,
    SessionWithMembership
)
from app.session.session_service import (
    create_session_service,
    update_session_service,
    invite_session_member_service,
    update_member_role_service,
    list_user_sessions_service
)

router = APIRouter()

@router.post("/", response_model=SessionResponse)
async def create_session_router(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_session_service(session_in, db, current_user)

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session_router(
    session_id: str,
    session_update: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_session_service(session_id, session_update, db, current_user)

@router.post("/invite", response_model=SessionMembershipResponse)
async def invite_user_router(
    invite: SessionMembershipInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await invite_session_member_service(invite, db, current_user)

@router.put("/access", response_model=SessionMembershipResponse)
async def change_access_router(
    access_update: SessionMembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_member_role_service(access_update, db, current_user)

@router.get("/list", response_model=list[SessionWithMembership])
async def list_sessions_router(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await list_user_sessions_service(db, current_user)