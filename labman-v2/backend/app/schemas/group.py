from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Group Schemas
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    lead_id: Optional[int] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    lead_id: Optional[int] = None

class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    has_project: bool = False
    
    class Config:
        from_attributes = True

class GroupWithCounts(GroupResponse):
    member_count: int = 0
    
# UserGroup Schemas
class UserGroupCreate(BaseModel):
    user_id: int

class UserGroupResponse(BaseModel):
    id: int
    user_id: int
    group_id: int
    joined_at: datetime
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    class Config:
        from_attributes = True

# Group Tree Node
class GroupTreeNode(BaseModel):
    id: int
    name: str
    description: Optional[str]
    lead_id: Optional[int]
    lead_name: Optional[str]
    member_count: int
    members: List['GroupTreeMember'] = []
    children: List['GroupTreeNode'] = []

class GroupTreeMember(BaseModel):
    user_id: int
    user_name: str
    user_email: str
