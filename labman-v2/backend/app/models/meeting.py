from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    meeting_time = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("research_groups.id"), nullable=True)
    is_private = Column(Integer, default=0)  # 0 for Public, 1 for Private
    tags = Column(String, nullable=True)  # Comma-separated tags
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    group = relationship("ResearchGroup", back_populates="meetings")
    responses = relationship("MeetingResponse", back_populates="meeting", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="meeting")


class MeetingResponse(Base):
    __tablename__ = "meeting_responses"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response = Column(String, nullable=False)  # 'join' or 'wont_join'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meeting = relationship("Meeting", back_populates="responses")
    user = relationship("User")
