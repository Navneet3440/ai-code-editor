from sqlalchemy.orm import Session
import argon2

from app.user.user_crud import create_user, get_user_by_username_or_email, get_user_by_username, get_all_users
from app.user.user_schema import UserCreateRequest





password_hasher = argon2.PasswordHasher()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except:
        return False


def register_user(db: Session, user_create: UserCreateRequest):
    # Check if the username or email already exists
    if get_user_by_username_or_email(db, user_create.username, user_create.email):
        return None 

    hashed = hash_password(user_create.password)
    user = create_user(
        db,
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed
    )
    return user


def login_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_all_users_service(db: Session):
    return get_all_users(db)