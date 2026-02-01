from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Server Schemas
class ServerBase(BaseModel):
    name: str
    hostname: str
    ip_address: str
    description: Optional[str] = None
    specs: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None

class ServerCreate(ServerBase):
    pass

class ServerUpdate(BaseModel):
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ServerResponse(ServerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
