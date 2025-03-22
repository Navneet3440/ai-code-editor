from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

from app.database import Base

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    created_by = Column(String, nullable=False)
    updated_by = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

class SessionMembership(Base):
    __tablename__ = 'session_memberships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # owner, editor, viewer
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False, nullable=False)