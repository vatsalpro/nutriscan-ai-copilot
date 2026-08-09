from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import ShoppingListItemDB

router = APIRouter(prefix="/api/shopping-list", tags=["shopping"])

class ShoppingItemCreate(BaseModel):
    ingredient: str
    quantity: float = 1.0
    unit: str = "g"

class BatchShoppingCreate(BaseModel):
    items: List[ShoppingItemCreate]

class ShoppingItemUpdate(BaseModel):
    purchased: Optional[bool] = None
    quantity: Optional[float] = None

@router.get("")
def get_shopping_list(db: Session = Depends(get_db)):
    items = db.query(ShoppingListItemDB).all()
    return items

@router.post("")
def add_shopping_item(item: ShoppingItemCreate, db: Session = Depends(get_db)):
    ing_name = item.ingredient.strip().lower()
    existing = db.query(ShoppingListItemDB).filter(ShoppingListItemDB.ingredient.ilike(ing_name)).first()
    if existing:
        existing.purchased = False
        db.commit()
        db.refresh(existing)
        return existing

    new_item = ShoppingListItemDB(
        user_id=1,
        ingredient=ing_name,
        quantity=item.quantity,
        unit=item.unit,
        purchased=False
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.post("/batch")
def add_batch_shopping_items(batch: BatchShoppingCreate, db: Session = Depends(get_db)):
    added_count = 0
    for item in batch.items:
        ing_name = item.ingredient.strip().lower()
        existing = db.query(ShoppingListItemDB).filter(ShoppingListItemDB.ingredient.ilike(ing_name)).first()
        if not existing:
            new_item = ShoppingListItemDB(
                user_id=1,
                ingredient=ing_name,
                quantity=item.quantity,
                unit=item.unit,
                purchased=False
            )
            db.add(new_item)
            added_count += 1
        else:
            existing.purchased = False

    db.commit()
    return {"message": f"Added {added_count} items to shopping list"}

@router.put("/{item_id}")
def update_shopping_item(item_id: int, update: ShoppingItemUpdate, db: Session = Depends(get_db)):
    item = db.query(ShoppingListItemDB).filter(ShoppingListItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    if update.purchased is not None:
        item.purchased = update.purchased
    if update.quantity is not None:
        item.quantity = update.quantity

    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}")
def delete_shopping_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ShoppingListItemDB).filter(ShoppingListItemDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shopping list item not found")

    db.delete(item)
    db.commit()
    return {"status": "deleted", "message": "Item deleted successfully", "id": item_id}
