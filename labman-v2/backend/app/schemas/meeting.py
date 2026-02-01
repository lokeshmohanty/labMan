from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Meeting Schemas
class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_time: datetime
    group_id: Optional[int] = None
    is_private: bool = False
    tags: Optional[str] = None  # Comma-separated
    summary: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_time: Optional[datetime] = None
    group_id: Optional[int] = None
    tags: Optional[str] = None
    summary: Optional[str] = None

class MeetingResponse(MeetingBase):
    id: int
    created_by: int
    created_at: datetime
    creator_name: Optional[str] = None
    group_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Meeting Response Schemas
class MeetingResponseCreate(BaseModel):
    response: str  # 'join' or 'wont_join'

class MeetingResponseData(BaseModel):
    id: int
    meeting_id: int
    user_id: int
    user_name: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Calendar Export
class CalendarLinks(BaseModel):
    google: str
    outlook: str
    ics: str
