from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ResearchGroup(Base):
    __tablename__ = "research_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("research_groups.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("ResearchGroup", remote_side=[id], backref="children")
    lead = relationship("User", foreign_keys=[lead_id])
    members = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="group")
    content = relationship("Content", back_populates="group")
    project = relationship("GroupProject", uselist=False, back_populates="group", cascade="all, delete-orphan")


class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id = Column(Integer, ForeignKey("research_groups.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="groups")
    group = relationship("ResearchGroup", back_populates="members")
