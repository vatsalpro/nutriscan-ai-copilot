from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

from database.database import get_db
from database.models import MealLogDB, RecipeDB

router = APIRouter(prefix="/api", tags=["nutrition"])

class MealCreateRequest(BaseModel):
    recipe_id: Optional[str] = None
    meal_name: str
    meal_type: Optional[str] = "Lunch" # Breakfast, Lunch, Snack, Dinner
    servings: Optional[float] = 1.0
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float

@router.get("/nutrition/today")
def get_today_nutrition(db: Session = Depends(get_db)):
    """
    Returns today's cumulative logged nutrition breakdown & meal timeline.
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    meals = db.query(MealLogDB).filter(MealLogDB.created_at >= today_start).all()

    total_calories = sum(m.calories for m in meals)
    total_protein = sum(m.protein for m in meals)
    total_carbs = sum(m.carbs for m in meals)
    total_fat = sum(m.fat for m in meals)
    total_fiber = sum(m.fiber for m in meals)

    # Defaults / Configurable Targets
    targets = {
        "calories": 2000,
        "protein": 75,
        "carbs": 250,
        "fat": 65,
        "fiber": 28
    }

    meal_list = []
    for m in meals:
        meal_list.append({
            "id": m.id,
            "recipe_id": m.recipe_id,
            "meal_name": m.meal_name,
            "meal_type": m.meal_type,
            "servings": m.servings,
            "calories": round(m.calories, 1),
            "protein": round(m.protein, 1),
            "carbs": round(m.carbs, 1),
            "fat": round(m.fat, 1),
            "fiber": round(m.fiber, 1),
            "time": m.created_at.strftime("%I:%M %p") if m.created_at else ""
        })

    totals = {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "carbs": round(total_carbs, 1),
        "fat": round(total_fat, 1),
        "fiber": round(total_fiber, 1)
    }

    return {
        "date": date.today().isoformat(),
        "totals": totals,
        # Kept for clients built against the original endpoint contract.
        "consumed": totals,
        "targets": targets,
        "progress": {
            "calories_pct": min(100, int((total_calories / targets["calories"]) * 100)),
            "protein_pct": min(100, int((total_protein / targets["protein"]) * 100)),
            "carbs_pct": min(100, int((total_carbs / targets["carbs"]) * 100)),
            "fat_pct": min(100, int((total_fat / targets["fat"]) * 100)),
            "fiber_pct": min(100, int((total_fiber / targets["fiber"]) * 100))
        },
        "logged_meals": meal_list
    }

@router.post("/meals")
def log_meal(req: MealCreateRequest, db: Session = Depends(get_db)):
    meal = MealLogDB(
        user_id=1,
        recipe_id=req.recipe_id,
        meal_name=req.meal_name,
        meal_type=req.meal_type or "Lunch",
        servings=req.servings or 1.0,
        calories=req.calories,
        protein=req.protein,
        carbs=req.carbs,
        fat=req.fat,
        fiber=req.fiber
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    meal_data = {
        "id": meal.id,
        "recipe_id": meal.recipe_id,
        "meal_name": meal.meal_name,
        "meal_type": meal.meal_type,
        "servings": meal.servings,
        "calories": meal.calories,
        "protein": meal.protein,
        "carbs": meal.carbs,
        "fat": meal.fat,
        "fiber": meal.fiber,
    }
    return {"message": "Meal logged successfully", "meal": meal_data, **meal_data}
