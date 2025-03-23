import uuid
from datetime import datetime, timezone
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.session.session_model import Session, SessionMembership, RoleEnum

def create_session(db: Session, name: str, content_type: str, content: str, created_by: str):
    new_session = Session(
        session_id=str(uuid.uuid4()),
        name=name,
        content_type=content_type,
        content=content,
        created_by=created_by,
        updated_by=created_by,
        is_deleted=False
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_session_by_id(db: Session, session_id: str, include_deleted: bool = False):
    query = db.query(Session).filter(Session.session_id == session_id)
    if not include_deleted:
        query = query.filter(Session.is_deleted == False)
    return query.first()

def update_session(db: Session, session_id: str, name: str = None, content_type: str = None, 
                  content: str = None, updated_by: str = None):
    session = get_session_by_id(db, session_id)
    if not session:
        return None
    
    if name is not None:
        session.name = name
    if content_type is not None:
        session.content_type = content_type
    if content is not None:
        session.content = content
    if updated_by is not None:
        session.updated_by = updated_by
    
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

def soft_delete_session(db: Session, session_id: str, deleted_by: str):
    session = get_session_by_id(db, session_id)
    if session:
        session.is_deleted = True
        session.updated_at = datetime.now(timezone.utc)
        session.updated_by = deleted_by
        db.commit()
        db.refresh(session)
    return session

def restore_session(db: Session, session_id: str, restored_by: str):
    session = db.query(Session).filter(
        Session.session_id == session_id,
        Session.is_deleted == True
    ).first()
    if session:
        session.is_deleted = False
        session.updated_at = datetime.now(timezone.utc)
        session.updated_by = restored_by
        db.commit()
        db.refresh(session)
    return session

def add_session_member(db: Session, user_id: str, session_id: str, role: str):
    role = RoleEnum(role)
    membership = SessionMembership(
        user_id=user_id,
        session_id=session_id,
        role=role,
        is_deleted=False
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

def update_member_role(db: Session, user_id: str, session_id: str, new_role: str):
    membership = db.query(SessionMembership).filter(
        SessionMembership.user_id == user_id,
        SessionMembership.session_id == session_id,
        SessionMembership.is_deleted == False
    ).first()
    if membership:
        membership.role = RoleEnum(new_role)
        membership.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(membership)
        return membership

def remove_session_member(db: Session, user_id: str, session_id: str):
    membership = db.query(SessionMembership).filter(
        SessionMembership.user_id == user_id,
        SessionMembership.session_id == session_id,
        SessionMembership.is_deleted == False
    ).first()
    if membership:
        membership.is_deleted = True
        membership.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(membership)
    return membership

def get_session_member(db: Session, user_id: str, session_id: str):
    return db.query(SessionMembership).filter(
        SessionMembership.user_id == user_id,
        SessionMembership.session_id == session_id,
        SessionMembership.is_deleted == False
    ).first()

def check_user_session_access(db: Session, user_id: str, session_id: str, roles: list = ["owner", "editor"]):
    member = get_session_member(db, user_id, session_id)
    return member and member.role.value in roles

def get_user_sessions(db: Session, user_id: str, include_deleted: bool = False):
    query = db.query(Session).join(
        SessionMembership,
        and_(
            Session.session_id == SessionMembership.session_id,
            SessionMembership.user_id == user_id,
            SessionMembership.is_deleted == False
        )
    )
    if not include_deleted:
        query = query.filter(Session.is_deleted == False)
    return query.all()
