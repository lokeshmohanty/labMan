from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Content Schemas
class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    group_id: Optional[int] = None
    meeting_id: Optional[int] = None
    research_plan_id: Optional[int] = None
    access_level: str = "group"  # 'group', 'public', 'private'

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    access_level: Optional[str] = None

class ContentResponse(ContentBase):
    id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    uploaded_by: int
    uploader_name: Optional[str] = None
    share_link: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
