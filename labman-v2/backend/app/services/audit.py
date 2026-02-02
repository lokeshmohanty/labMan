from sqlalchemy.orm import Session
from app.models import AuditLog, User
from datetime import datetime
from typing import Optional, List

def log_action(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    details: Optional[str] = None
):
    """Log an action to the audit log"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log

def get_audit_logs(
    db: Session,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    """Get audit logs with optional filters"""
    query = db.query(AuditLog)
    
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(AuditLog.action.contains(action))
    
    query = query.order_by(AuditLog.created_at.desc())
    
    return query.offset(skip).limit(limit).all()
