from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models import Server, User
from app.schemas.server import ServerCreate, ServerUpdate, ServerResponse

router = APIRouter()

@router.get("/", response_model=List[ServerResponse])
async def list_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """List all servers"""
    servers = db.query(Server).order_by(Server.name).offset(skip).limit(limit).all()
    return servers

@router.post("/", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new server (admin only)"""
    db_server = Server(
        name=server_data.name,
        hostname=server_data.hostname,
        ip_address=server_data.ip_address,
        description=server_data.description,
        specs=server_data.specs,
        status=server_data.status,
        notes=server_data.notes
    )
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    return db_server

@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get server by ID"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server

@router.put("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_data: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update server"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Update fields
    if server_data.name is not None:
        server.name = server_data.name
    if server_data.hostname is not None:
        server.hostname = server_data.hostname
    if server_data.ip_address is not None:
        server.ip_address = server_data.ip_address
    if server_data.description is not None:
        server.description = server_data.description
    if server_data.specs is not None:
        server.specs = server_data.specs
    if server_data.status is not None:
        server.status = server_data.status
    if server_data.notes is not None:
        server.notes = server_data.notes
    
    db.commit()
    db.refresh(server)
    return server

@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete server (admin only)"""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db.delete(server)
    db.commit()
    return None
