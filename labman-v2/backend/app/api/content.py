from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import Content, User
from app.schemas.content import ContentCreate, ContentUpdate, ContentResponse
from app.services.file_storage import save_upload_file, delete_file, get_file_path
from pathlib import Path

router = APIRouter()

@router.get("/", response_model=List[ContentResponse])
async def list_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    group_id: int = None,
    research_plan_id: int = None
):
    """List all content"""
    query = db.query(Content)
    
    if group_id:
        query = query.filter(Content.group_id == group_id)
    if research_plan_id:
        query = query.filter(Content.research_plan_id == research_plan_id)
    
    content = query.order_by(Content.created_at.desc()).offset(skip).limit(limit).all()
    return content

@router.post("/upload", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_content(
    file: UploadFile = File(...),
    title: str = None,
    description: str = None,
    group_id: int = None,
    research_plan_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file"""
    # Save file
    filename = await save_upload_file(file)
    
    # Create content record
    db_content = Content(
        title=title or file.filename,
        description=description,
        filename=filename,
        original_filename=file.filename,
        file_size=file.size if hasattr(file, 'size') else 0,
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        group_id=group_id,
        research_plan_id=research_plan_id
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return db_content

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get content by ID"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    content_data: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update content metadata"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Only uploader or admin can update
    if content.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the uploader or admin can update this content"
        )
    
    # Update fields
    if content_data.title is not None:
        content.title = content_data.title
    if content_data.description is not None:
        content.description = content_data.description
    if content_data.group_id is not None:
        content.group_id = content_data.group_id
    if content_data.research_plan_id is not None:
        content.research_plan_id = content_data.research_plan_id
    
    db.commit()
    db.refresh(content)
    return content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete content"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Only uploader or admin can delete
    if content.uploaded_by != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the uploader or admin can delete this content"
        )
    
    # Delete file from storage
    try:
        delete_file(content.filename)
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    db.delete(content)
    db.commit()
    return None

@router.get("/{content_id}/download")
async def download_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a file"""
    from fastapi.responses import FileResponse
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    file_path = get_file_path(content.filename)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=content.original_filename,
        media_type=content.mime_type
    )
