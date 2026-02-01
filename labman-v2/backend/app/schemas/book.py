from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    quantity: int = 1
    status: str = "available"
    location: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
