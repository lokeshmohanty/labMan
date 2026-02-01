from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models import Inventory, User
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse

router = APIRouter()

@router.get("/", response_model=List[InventoryResponse])
async def list_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    available_only: bool = False
):
    """List all inventory items"""
    query = db.query(Inventory)
    
    if available_only:
        query = query.filter(Inventory.status == "available")
    
    items = query.order_by(Inventory.name).offset(skip).limit(limit).all()
    return items

@router.post("/", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_data: InventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new inventory item"""
    db_item = Inventory(
        name=item_data.name,
        description=item_data.description,
        quantity=item_data.quantity,
        location=item_data.location,
        status=item_data.status,
        notes=item_data.notes
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=InventoryResponse)
async def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory item by ID"""
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@router.put("/{item_id}", response_model=InventoryResponse)
async def update_inventory_item(
    item_id: int,
    item_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inventory item"""
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Update fields
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.description is not None:
        item.description = item_data.description
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    if item_data.location is not None:
        item.location = item_data.location
    if item_data.status is not None:
        item.status = item_data.status
    if item_data.notes is not None:
        item.notes = item_data.notes
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete inventory item (admin only)"""
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db.delete(item)
    db.commit()
    return None
