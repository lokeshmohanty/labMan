from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("research_groups.id"), nullable=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=True)
    research_plan_id = Column(Integer, ForeignKey("research_plans.user_id"), nullable=True)
    access_level = Column(String, default="group")  # 'group', 'public', 'private'
    share_link = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    group = relationship("ResearchGroup", back_populates="content")
    meeting = relationship("Meeting", back_populates="content")
    research_plan = relationship("ResearchPlan", back_populates="content")
