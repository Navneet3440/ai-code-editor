from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth_helper import get_current_user, User
from app.database import get_db
from app.session.session_schema import (
    SessionCreate,
    SessionUpdate,
    SessionMembershipInvite,
    SessionMembershipUpdate,
    SessionResponse,
    SessionMembershipResponse,
    SessionWithMembership,
    RoleEnum
)
from app.session.session_service import (
    create_session_service,
    update_session_service,
    invite_session_member_service,
    update_member_role_service,
    list_user_sessions_service,
    get_session_user_map
)

router = APIRouter()

@router.post("/", response_model=SessionResponse)
def create_session_router(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_in.created_by = current_user.user_id
    session_instance = create_session_service(db, session_in)
    if not session_instance:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Session creation failed")
    return session_instance

@router.put("/access", response_model=SessionMembershipResponse)
def change_access_router(
    access_update: SessionMembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_user_membership = get_session_user_map(db, access_update.session_id, current_user.user_id)
    if (not session_user_membership) or (session_user_membership.role != RoleEnum.OWNER):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User dosent have acess to invite. Only Owner can Invite"
            )
    return update_member_role_service(db, access_update)

@router.put("/{session_id}", response_model=SessionResponse)
def update_session_router(
    session_id: str,
    session_update: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_user_membership = get_session_user_map(db, session_id, current_user.user_id)
    if (not session_user_membership) or (session_user_membership == RoleEnum.VIEWER):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User dosent have acess to update")
    session_update.updated_by = current_user.user_id
    session_instance = update_session_service(db, session_id, session_update)
    if not session_instance:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Session update failed")
    return session_instance

@router.post("/invite", response_model=SessionMembershipResponse)
def invite_user_router(
    invite: SessionMembershipInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_user_membership = get_session_user_map(db, invite.session_id, current_user.user_id)
    if (not session_user_membership) or (session_user_membership.role != RoleEnum.OWNER):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User dosent have acess to invite. Only Owner can Invite"
            )
    session_new_user_map = get_session_user_map(db, invite.session_id, invite.user_id)
    if session_new_user_map:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User already invited"
        )
    return invite_session_member_service(db, invite)


@router.get("/list", response_model=list[SessionWithMembership])
def list_sessions_router(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return list_user_sessions_service(db, current_user.user_id)