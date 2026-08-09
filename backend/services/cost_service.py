from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import IngredientDB

class CostService:
    @staticmethod
    def calculate_recipe_cost(db: Session, ingredients: List[Dict[str, Any]], default_cost: float = 100.0) -> Dict[str, Any]:
        """
        Calculates estimated total cost in INR (₹) and cost per serving.
        """
        calculated_total = 0.0
        has_items = False

        for item in ingredients:
            ing_name = str(item.get("ingredient") or item.get("name") or "").lower().strip()
            qty = float(item.get("quantity") or item.get("estimated_quantity") or 0.0)
            
            db_ing = db.query(IngredientDB).filter(IngredientDB.id == ing_name).first()
            if db_ing and db_ing.price_per_unit > 0:
                has_items = True
                calculated_total += qty * db_ing.price_per_unit

        final_total = round(calculated_total if has_items and calculated_total > 10 else default_cost, 1)

        return {
            "estimated_cost_total": final_total,
            "currency": "₹",
            "disclaimer": "Prices are estimates for reference and may vary by location, brand, and season."
        }

cost_service = CostService()
