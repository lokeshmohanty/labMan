from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# Research Plan Schemas
class ResearchPlanBase(BaseModel):
    problem_statement: Optional[str] = None
    research_progress: Optional[str] = None
    github_link: Optional[str] = None
    manuscript_link: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    comments: Optional[str] = None

class ResearchPlanUpdate(ResearchPlanBase):
    pass

class ResearchPlanResponse(ResearchPlanBase):
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Research Task Schemas
class ResearchTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "pending"  # 'pending', 'in_progress', 'completed'

class ResearchTaskCreate(ResearchTaskBase):
    pass

class ResearchTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class ResearchTaskResponse(ResearchTaskBase):
    id: int
    plan_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Combined Research Plan with Tasks
class ResearchPlanWithTasks(ResearchPlanResponse):
    tasks: List[ResearchTaskResponse] = []
