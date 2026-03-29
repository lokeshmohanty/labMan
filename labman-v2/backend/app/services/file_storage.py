import os
import aiofiles
from pathlib import Path
from typing import Optional
import secrets
from fastapi import UploadFile

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.md',
    '.jpg', '.jpeg', '.png', '.gif', '.svg',
    '.zip', '.tar', '.gz',
    '.csv', '.xlsx', '.xls',
    '.py', '.ipynb', '.json', '.yaml', '.yml'
}

BLOCKED_EXTENSIONS = {
    '.exe', '.sh', '.bat', '.cmd', '.com', '.scr'
}

async def save_upload_file(file: UploadFile, subfolder: str = "") -> tuple[str, int]:
    """
    Save an uploaded file and return (file_path, file_size)
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext in BLOCKED_EXTENSIONS:
        raise ValueError(f"File type {file_ext} is not allowed")
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {file_ext} is not supported")
    
    # Generate unique filename
    random_name = secrets.token_hex(16)
    filename = f"{random_name}{file_ext}"
    
    # Create subfolder if specified
    save_dir = UPLOAD_DIR / subfolder if subfolder else UPLOAD_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = save_dir / filename
    
    # Save file
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
            await f.write(chunk)
            file_size += len(chunk)
    
    # Return relative path from UPLOAD_DIR
    relative_path = str(file_path.relative_to(UPLOAD_DIR.parent))
    return relative_path, file_size

async def delete_file(filename: str) -> None:
    """Delete a file from storage"""
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()

def get_file_path(filename: str) -> Path:
    """Get the full path to a file"""
    return UPLOAD_DIR / filename

def generate_share_link() -> str:
    """Generate a unique share link"""
    return secrets.token_urlsafe(32)
