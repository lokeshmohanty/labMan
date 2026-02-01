from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas.audit import AuditLogResponse
from app.services.audit import get_audit_logs

router = APIRouter()

@router.get("/logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """Get audit logs with optional filters"""
    logs = get_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        skip=skip,
        limit=limit
    )
    
    # Enrich with user names
    result = []
    for log in logs:
        user_name = None
        if log.user_id:
            user = db.query(User).filter(User.id == log.user_id).first()
            if user:
                user_name = user.name
        
        result.append(AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=user_name,
            action=log.action,
            details=log.details,
            created_at=log.created_at
        ))
    
    return result
