import uuid
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.user.user_model import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(
        User.username == username,
        User.is_deleted == False
    ).first()

def get_user_by_username_or_email(db: Session, username: str = None, email: str = None):
    return db.query(User).filter(
        or_(User.username == username, User.email == email),
        User.is_deleted == False
    ).first()

def get_user_by_user_id(db: Session, user_id: str):
    return db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == False
    ).first()

def get_all_users(db: Session, include_deleted: bool = False):
    query = db.query(User)
    if not include_deleted:
        query = query.filter(User.is_deleted == False)
    return query.all()

def create_user(db: Session, username: str, email: str, hashed_password: str):
    user = User(
        user_id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_deleted=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def soft_delete_user(db: Session, user_id: str):
    user = get_user_by_user_id(db, user_id)
    if user:
        user.is_deleted = True
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user

def restore_user(db: Session, user_id: str):
    user = db.query(User).filter(
        User.user_id == user_id,
        User.is_deleted == True
    ).first()
    if user:
        user.is_deleted = False
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user
