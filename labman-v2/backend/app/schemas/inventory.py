from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Inventory Schemas
class InventoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 0
    location: Optional[str] = None
    status: str = "available"
    notes: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class InventoryResponse(InventoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
