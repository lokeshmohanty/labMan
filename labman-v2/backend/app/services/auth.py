from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User, PasswordResetToken
from app.config import get_settings
import secrets

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # DEVELOPMENT ONLY: Plain text password comparison
    # TODO: Re-enable bcrypt for production
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # DEVELOPMENT ONLY: Return plain text password
    # TODO: Re-enable bcrypt for production
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode JWT access token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.password_hash:
        return None  # Account not activated
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_password_reset_token(db: Session, user_id: int) -> str:
    """Create a password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    db_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def verify_reset_token(db: Session, token: str) -> Optional[int]:
    """Verify a password reset token and return user_id"""
    db_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        return None
    
    return db_token.user_id

def mark_token_used(db: Session, token: str):
    """Mark a token as used"""
    db_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if db_token:
        db_token.used = True
        db.commit()
