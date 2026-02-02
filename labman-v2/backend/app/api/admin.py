from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import tomli
import tomli_w
import os
from datetime import datetime
from app.api.deps import get_current_user
from app.models import User
from app.config import get_settings

router = APIRouter()

CONFIG_PATH = "data/config.toml"

@router.post("/config/reload")
async def reload_config(
    current_user: User = Depends(get_current_user)
):
    """Reload configuration from file"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reload configuration"
        )
    
    try:
        get_settings.cache_clear()
        return {"message": "Configuration reloaded successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading configuration: {str(e)}"
        )

class ConfigUpdate(BaseModel):
    content: str

@router.get("/config")
async def get_config(
    current_user: User = Depends(get_current_user)
):
    """Get the current configuration file content"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access configuration"
        )
    
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration file not found"
        )
        
    try:
        with open(CONFIG_PATH, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading configuration: {str(e)}"
        )

@router.put("/config")
async def update_config(
    config_data: ConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update the configuration file"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update configuration"
        )
        
    # Validate TOML syntax
    try:
        tomli.loads(config_data.content)
    except tomli.TOMLDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid TOML syntax: {str(e)}"
        )
        
    try:
        with open(CONFIG_PATH, "w") as f:
            f.write(config_data.content)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error writing configuration: {str(e)}"
        )
@router.get("/config/structured")
async def get_structured_config(
    current_user: User = Depends(get_current_user)
):
    """Get the current configuration as JSON"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access configuration"
        )
    
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration file not found"
        )
        
    try:
        with open(CONFIG_PATH, "rb") as f:
            content = tomli.load(f)
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading configuration: {str(e)}"
        )

@router.put("/config/structured")
async def update_structured_config(
    config_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update the configuration from JSON"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update configuration"
        )
        
    try:
        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(config_data, f)
        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error writing configuration: {str(e)}"
        )

BACKUP_DIR = "data/backups"

@router.post("/config/backup")
async def create_backup(
    current_user: User = Depends(get_current_user)
):
    """Create a backup of the current configuration"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create backups"
        )
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"config_backup_{timestamp}.toml")
    
    try:
        import shutil
        shutil.copy2(CONFIG_PATH, backup_path)
        return {"message": "Backup created successfully", "filename": os.path.basename(backup_path)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating backup: {str(e)}"
        )

@router.get("/config/backups")
async def list_backups(
    current_user: User = Depends(get_current_user)
):
    """List available configuration backups"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view backups"
        )
    
    if not os.path.exists(BACKUP_DIR):
        return []
        
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".toml"):
            path = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(path)
            backups.append({
                "filename": filename,
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            })
    
    # Sort by creation time descending
    backups.sort(key=lambda x: x["created_at"], reverse=True)

    return backups

@router.get("/config/backups/{filename}")
async def get_backup_content(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Get the content of a specific backup file"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view backups"
        )
    
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    # simple path traversal check
    if not os.path.abspath(backup_path).startswith(os.path.abspath(BACKUP_DIR)):
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    if not os.path.exists(backup_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup file not found"
        )
        
    try:
        with open(backup_path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading backup: {str(e)}"
        )

@router.post("/config/restore/{filename}")
async def restore_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Restore configuration from a backup"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can restore backups"
        )
    
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    # simple path traversal check
    if not os.path.abspath(backup_path).startswith(os.path.abspath(BACKUP_DIR)):
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )

    if not os.path.exists(backup_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup file not found"
        )
        
    try:
        import shutil
        shutil.copy2(backup_path, CONFIG_PATH)
        # Clear cache so new settings apply where possible
        get_settings.cache_clear()
        return {"message": "Configuration restored successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring backup: {str(e)}"
        )
