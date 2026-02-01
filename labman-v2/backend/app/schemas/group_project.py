from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Group Project Schemas
class GroupProjectBase(BaseModel):
    problem_statement: Optional[str] = None
    research_progress: Optional[str] = None
    github_link: Optional[str] = None
    manuscript_link: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    comments: Optional[str] = None

class GroupProjectUpdate(GroupProjectBase):
    pass

class GroupTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "pending"

class GroupTaskCreate(GroupTaskBase):
    pass

class GroupTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class GroupTaskResponse(GroupTaskBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GroupProjectResponse(GroupProjectBase):
    group_id: int
    updated_at: datetime
    tasks: List[GroupTaskResponse] = []

    class Config:
        from_attributes = True
