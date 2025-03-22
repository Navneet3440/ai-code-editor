from sqlalchemy.orm import Session
from app.session.session_crud import (
    create_session,
    update_session,
    add_session_member,
    update_member_role,
    get_user_sessions
)
from app.session.session_schema import (
    SessionCreate,
    SessionUpdate,
    SessionMembershipInvite,
    SessionMembershipUpdate
)


def create_session_service(db: Session, session_in: SessionCreate):
    # Create a new session
    session = create_session(
        db=db,
        name=session_in.name,
        content_type=session_in.content_type,
        content=session_in.content,
        created_by=session_in.created_by
    )
    # Provide access to the user who created the session
    add_session_member(
        db=db,
        user_id=session.created_by,
        session_id=session.session_id,
        role="owner"
    )
    return session

def update_session_service(db: Session, session_id: str, session_update: SessionUpdate):
    return update_session(
        db=db,
        session_id=session_id,
        name=session_update.name,
        content_type=session_update.content_type,
        content=session_update.content,
        updated_by=session_update.updated_by
    )
    
def invite_session_member_service(db: Session, invite: SessionMembershipInvite):
    return add_session_member(
        db=db,
        user_id=invite.user_id,
        session_id=invite.session_id,
        role=invite.role
    )

def update_member_role_service(db: Session, update: SessionMembershipUpdate):
    return update_member_role(
        db=db,
        user_id=update.user_id,
        session_id=update.session_id,
        new_role=update.role
    )


def list_user_sessions_service(db: Session, user_id: str):
    return get_user_sessions(db, user_id)