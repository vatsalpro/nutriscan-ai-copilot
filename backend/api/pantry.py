from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import PantryItem, IngredientDB

router = APIRouter(prefix="/api/pantry", tags=["pantry"])

class PantryItemCreate(BaseModel):
    ingredient: str
    quantity: float = 100.0
    unit: str = "g"
    freshness: str = "Fresh" # "Fresh", "Use Soon", "Expiring Soon"

class PantryItemUpdate(BaseModel):
    quantity: Optional[float] = None
    unit: Optional[str] = None
    freshness: Optional[str] = None

@router.get("")
def get_pantry(db: Session = Depends(get_db)):
    items = db.query(PantryItem).all()
    results = []
    for item in items:
        # Fetch icon if available in ingredient DB
        ing = db.query(IngredientDB).filter(IngredientDB.id == item.ingredient.lower()).first()
        icon = ing.icon if ing else "🥗"
        results.append({
            "id": item.id,
            "ingredient": item.ingredient,
            "quantity": item.quantity,
            "unit": item.unit,
            "freshness": item.freshness,
            "icon": icon,
            "created_at": item.created_at.isoformat() if item.created_at else ""
        })
    return results

@router.post("")
def add_pantry_item(item: PantryItemCreate, db: Session = Depends(get_db)):
    ing_name = item.ingredient.strip().lower()
    # Check if already exists in pantry
    existing = db.query(PantryItem).filter(PantryItem.ingredient.ilike(ing_name)).first()
    if existing:
        existing.quantity += item.quantity
        existing.freshness = item.freshness
        db.commit()
        db.refresh(existing)
        return {"message": "Updated existing pantry item", "item": existing}

    new_item = PantryItem(
        user_id=1,
        ingredient=ing_name,
        quantity=item.quantity,
        unit=item.unit,
        freshness=item.freshness
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/{item_id}")
def update_pantry_item(item_id: int, update: PantryItemUpdate, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    if update.quantity is not None:
        item.quantity = update.quantity
    if update.unit is not None:
        item.unit = update.unit
    if update.freshness is not None:
        item.freshness = update.freshness

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pantry item not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted", "message": "Pantry item deleted successfully", "id": item_id}
