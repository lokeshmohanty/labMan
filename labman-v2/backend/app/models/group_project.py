from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class GroupProject(Base):
    """Group project page - similar to research plan but for groups"""
    __tablename__ = "group_projects"

    group_id = Column(Integer, ForeignKey("research_groups.id", ondelete="CASCADE"), primary_key=True)
    problem_statement = Column(Text, nullable=True)
    research_progress = Column(Text, nullable=True)
    github_link = Column(String, nullable=True)
    manuscript_link = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    comments = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("ResearchGroup", back_populates="project")
    tasks = relationship("GroupTask", back_populates="project", cascade="all, delete-orphan")

class GroupTask(Base):
    """Tasks for group projects"""
    __tablename__ = "group_tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("group_projects.group_id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("GroupProject", back_populates="tasks")
