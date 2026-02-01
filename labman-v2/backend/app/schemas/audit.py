from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    user_name: Optional[str]
    action: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
