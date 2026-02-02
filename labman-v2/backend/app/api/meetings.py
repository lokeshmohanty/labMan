from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from app.api.deps import get_db, get_current_user
from app.models import Meeting, MeetingResponse as MeetingResponseModel, User
from app.schemas.meeting import (
    MeetingCreate, MeetingUpdate, MeetingResponse,
    MeetingResponseCreate, MeetingResponseData
)

router = APIRouter()

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    upcoming: bool = False
):
    """List all meetings"""
    # Privacy filtering:
    # 1. Public meetings (is_private == 0)
    # 2. Private meetings where user is creator
    # 3. Private meetings where user is in the group
    # 4. Admins see everything
    
    if current_user.is_admin:
        query = db.query(Meeting)
    else:
        from app.models.group import UserGroup
        group_ids = db.query(UserGroup.group_id).filter(UserGroup.user_id == current_user.id).all()
        group_ids = [id[0] for id in group_ids]
        
        query = db.query(Meeting).filter(
            or_(
                Meeting.is_private == 0,
                Meeting.created_by == current_user.id,
                Meeting.group_id.in_(group_ids)
            )
        )
    
    if upcoming:
        query = query.filter(Meeting.meeting_time >= datetime.utcnow())
    
    meetings = query.order_by(Meeting.meeting_time.desc()).offset(skip).limit(limit).all()
    
    # Add creator and group names
    for meeting in meetings:
        if meeting.created_by:
            creator = db.query(User).filter(User.id == meeting.created_by).first()
            meeting.creator_name = creator.name if creator else None
        if meeting.group_id:
            from app.models import ResearchGroup
            group = db.query(ResearchGroup).filter(ResearchGroup.id == meeting.group_id).first()
            meeting.group_name = group.name if group else None
    
    return meetings

@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new meeting"""
    db_meeting = Meeting(
        title=meeting_data.title,
        description=meeting_data.description,
        meeting_time=meeting_data.meeting_time,
        group_id=meeting_data.group_id,
        is_private=1 if meeting_data.is_private else 0,
        tags=meeting_data.tags,
        summary=meeting_data.summary,
        created_by=current_user.id
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    # Add creator name
    db_meeting.creator_name = current_user.name
    
    return db_meeting

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get meeting by ID"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Privacy check
    if meeting.is_private == 1 and not current_user.is_admin and meeting.created_by != current_user.id:
        from app.models.group import UserGroup
        is_member = db.query(UserGroup).filter(
            UserGroup.group_id == meeting.group_id,
            UserGroup.user_id == current_user.id
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this private meeting"
            )
    
    # Add creator and group names
    if meeting.created_by:
        creator = db.query(User).filter(User.id == meeting.created_by).first()
        meeting.creator_name = creator.name if creator else None
    if meeting.group_id:
        from app.models import ResearchGroup
        group = db.query(ResearchGroup).filter(ResearchGroup.id == meeting.group_id).first()
        meeting.group_name = group.name if group else None
    
    return meeting

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Only creator or admin can update
    if meeting.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can update this meeting"
        )
    
    # Update fields
    if meeting_data.title is not None:
        meeting.title = meeting_data.title
    if meeting_data.description is not None:
        meeting.description = meeting_data.description
    if meeting_data.meeting_time is not None:
        meeting.meeting_time = meeting_data.meeting_time
    if meeting_data.group_id is not None:
        meeting.group_id = meeting_data.group_id
    if meeting_data.tags is not None:
        meeting.tags = meeting_data.tags
    if meeting_data.summary is not None:
        meeting.summary = meeting_data.summary
    if meeting_data.is_private is not None:
        meeting.is_private = 1 if meeting_data.is_private else 0
    
    db.commit()
    db.refresh(meeting)
    return meeting

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Only creator or admin can delete
    if meeting.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator or admin can delete this meeting"
        )
    
    db.delete(meeting)
    db.commit()
    return None

# RSVP Endpoints

@router.get("/{meeting_id}/responses", response_model=List[MeetingResponseData])
async def get_meeting_responses(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all responses for a meeting"""
    responses = db.query(MeetingResponseModel).filter(
        MeetingResponseModel.meeting_id == meeting_id
    ).all()
    
    # Add user names
    result = []
    for resp in responses:
        user = db.query(User).filter(User.id == resp.user_id).first()
        result.append(MeetingResponseData(
            id=resp.id,
            meeting_id=resp.meeting_id,
            user_id=resp.user_id,
            user_name=user.name if user else "Unknown",
            response=resp.response,
            created_at=resp.created_at
        ))
    
    return result

@router.post("/{meeting_id}/respond", response_model=MeetingResponseData, status_code=status.HTTP_201_CREATED)
async def respond_to_meeting(
    meeting_id: int,
    response_data: MeetingResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Respond to a meeting (RSVP)"""
    # Check if meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check if user already responded
    existing = db.query(MeetingResponseModel).filter(
        MeetingResponseModel.meeting_id == meeting_id,
        MeetingResponseModel.user_id == current_user.id
    ).first()
    
    if existing:
        # Update existing response
        existing.response = response_data.response
        db.commit()
        db.refresh(existing)
        return MeetingResponseData(
            id=existing.id,
            meeting_id=existing.meeting_id,
            user_id=existing.user_id,
            user_name=current_user.name,
            response=existing.response,
            created_at=existing.created_at
        )
    else:
        # Create new response
        db_response = MeetingResponseModel(
            meeting_id=meeting_id,
            user_id=current_user.id,
            response=response_data.response
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        
        return MeetingResponseData(
            id=db_response.id,
            meeting_id=db_response.meeting_id,
            user_id=db_response.user_id,
            user_name=current_user.name,
            response=db_response.response,
            created_at=db_response.created_at
        )
