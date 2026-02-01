from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    email_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")
    research_plan = relationship("ResearchPlan", uselist=False, back_populates="user", cascade="all, delete-orphan")
