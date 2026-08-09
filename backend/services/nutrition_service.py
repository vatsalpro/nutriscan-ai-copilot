import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.models import IngredientDB

logger = logging.getLogger(__name__)


class NutritionService:
    """Local/deterministic nutrition calculations. AI is not required here."""

    def __init__(self):
        self.food_db = {
            "apple": {"calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "fiber": 2.4},
            "banana": {"calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "fiber": 2.6},
            "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2},
            "paneer": {"calories": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8, "fiber": 0},
            "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0},
            "oats": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "fiber": 10.6},
            "egg": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0},
            "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4},
            "potato": {"calories": 77, "protein": 2, "carbs": 17.5, "fat": 0.1, "fiber": 2.2},
            "carrot": {"calories": 41, "protein": 0.9, "carbs": 9.6, "fat": 0.2, "fiber": 2.8},
        }

    def ensure_ingredient_exists(self, db: Session, name: str, unit: str = "g"):
        name_clean = name.lower().strip()
        if not name_clean:
            return None
        existing = db.query(IngredientDB).filter(
            (IngredientDB.id == name_clean) | (func.lower(IngredientDB.name) == name_clean)
        ).first()
        if existing:
            return existing

        food_data = self.food_db.get(
            name_clean,
            {"calories": 50.0, "protein": 1.5, "carbs": 8.0, "fat": 0.5, "fiber": 1.0}
        )
        new_ing = IngredientDB(
            id=name_clean,
            name=name.title(),
            category="General",
            unit=unit,
            calories=food_data["calories"],
            protein=food_data["protein"],
            carbs=food_data["carbs"],
            fat=food_data["fat"],
            fiber=food_data["fiber"],
            price_per_unit=0.2,
            icon="🥗"
        )
        db.add(new_ing)
        db.commit()
        db.refresh(new_ing)
        return new_ing

    def calculate_recipe_nutrition(self, db: Session, ingredients: list, servings: int = 2) -> dict:
        servings = max(1, int(servings or 2))
        totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "fiber": 0.0}
        details = []

        for item in ingredients or []:
            if isinstance(item, str):
                ing_name, qty = item.lower().strip(), 100.0
            else:
                ing_name = str(item.get("ingredient") or item.get("name") or "").lower().strip()
                qty = float(item.get("quantity") or item.get("estimated_quantity") or 100.0)

            if not ing_name:
                continue

            db_ing = db.query(IngredientDB).filter(
                (IngredientDB.id == ing_name) | (func.lower(IngredientDB.name) == ing_name)
            ).first()

            if db_ing:
                cals, prot, carbs, fat, fib = db_ing.calories, db_ing.protein, db_ing.carbs, db_ing.fat, db_ing.fiber
            elif ing_name in self.food_db:
                f = self.food_db[ing_name]
                cals, prot, carbs, fat, fib = f["calories"], f["protein"], f["carbs"], f["fat"], f["fiber"]
            else:
                cals, prot, carbs, fat, fib = 50.0, 1.5, 8.0, 0.5, 1.0

            mult = qty / 100.0 if qty > 0 else 1.0
            item_nutr = {
                "calories": round(cals * mult, 1),
                "protein": round(prot * mult, 1),
                "carbs": round(carbs * mult, 1),
                "fat": round(fat * mult, 1),
                "fiber": round(fib * mult, 1),
            }
            for k in totals:
                totals[k] += item_nutr[k]
            details.append({"ingredient": ing_name, "quantity": qty, **item_nutr})

        per_serving = {k: round(v / servings, 1) for k, v in totals.items()}
        total = {k: round(v, 1) for k, v in totals.items()}

        return {
            "total": total,
            "total_recipe": total,
            "per_serving": per_serving,
            "details": details,
            "servings": servings
        }

    def calculate(self, ingredients):
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
        details = []

        for item in ingredients or []:
            if isinstance(item, str):
                name, quantity = item.lower().strip(), 100
            else:
                name = str(item.get("name") or item.get("ingredient") or "").lower().strip()
                quantity = item.get("quantity") or item.get("estimated_quantity") or 100

            if not name:
                continue
            try:
                grams = float(quantity)
            except (TypeError, ValueError):
                grams = 100.0

            food = self.food_db.get(name)
            if not food:
                continue

            multiplier = grams / 100.0
            item_nutrition = {k: round(v * multiplier, 2) for k, v in food.items()}
            for key in totals:
                totals[key] += item_nutrition[key]
            details.append({"name": name, "quantity_g": grams, **item_nutrition})

        return {
            **{k: round(v, 2) for k, v in totals.items()},
            "details": details,
            "source": "NutriScan local nutrition database",
        }


nutrition_service = NutritionService()

