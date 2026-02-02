from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas.user import (
    Token, LoginRequest, UserResponse, ActivateAccount,
    PasswordResetRequest, PasswordResetConfirm
)
from app.services.auth import (
    authenticate_user, create_access_token, get_password_hash,
    create_password_reset_token, verify_reset_token, mark_token_used
)
from app.services.email import send_activation_email, send_password_reset_email
from app.config import get_settings

settings = get_settings()
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint with JSON body"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    return current_user

@router.post("/activate")
async def activate_account(
    data: ActivateAccount,
    db: Session = Depends(get_db)
):
    """Activate user account with token"""
    user_id = verify_reset_token(db, data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Set password
    user.password_hash = get_password_hash(data.password)
    mark_token_used(db, data.token)
    db.commit()
    
    return {"message": "Account activated successfully"}

@router.post("/forgot-password")
async def forgot_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == data.email).first()
    
    # Always return success to prevent email enumeration
    if user:
        token = create_password_reset_token(db, user.id)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
        await send_password_reset_email(user.email, user.name, reset_link)
    
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    user_id = verify_reset_token(db, data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = get_password_hash(data.new_password)
    mark_token_used(db, data.token)
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.get("/system-info")
async def get_system_info():
    """Get public system information"""
    return {
        "lab_name": settings.LAB_NAME,
        "timezone": settings.TIMEZONE
    }
