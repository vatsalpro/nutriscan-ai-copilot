from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database.database import get_db
from database.models import IngredientDB, RecipeDB, RecipeIngredientDB
from services.recipe_service import recipe_service

from services.nutrition_service import nutrition_service
from services.scoring_service import scoring_service

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

class FindRecipesRequest(BaseModel):
    ingredients: List[Dict[str, Any]] = []
    filters: Optional[Dict[str, Any]] = {}
    include_pantry: Optional[bool] = True

class ImproveMealRequest(BaseModel):
    servings: Optional[int] = 2
    reduce_oil: Optional[bool] = True
    add_veggies: Optional[bool] = True
    boost_protein: Optional[bool] = False
    substitutions: Optional[Dict[str, str]] = {}

@router.post("/find")
def find_recipes(req: FindRecipesRequest, db: Session = Depends(get_db)):
    scanned_names = {
        str(item.get("name") or item.get("ingredient") or "").lower().strip()
        for item in req.ingredients
    }
    scanned_names.discard("")

    # Ensure all user/scanned ingredients exist in IngredientDB with default nutrition
    unknown_names = []
    for name in scanned_names:
        known = db.query(IngredientDB).filter(
            (IngredientDB.id == name) | (func.lower(IngredientDB.name) == name)
        ).first()
        if not known:
            unknown_names.append(name)
            nutrition_service.ensure_ingredient_exists(db, name, unit="g")

    generated_recipe = None
    if req.ingredients:
        # Check if an AI recipe for these exact ingredients was already created in DB
        existing_ai_recipe = None
        all_ai_recipes = db.query(RecipeDB).filter(RecipeDB.id.like("ai-recipe-%")).all()
        for rec in all_ai_recipes:
            rec_ings = db.query(RecipeIngredientDB).filter(RecipeIngredientDB.recipe_id == rec.id).all()
            rec_ing_names = set(r.ingredient.lower().strip() for r in rec_ings)
            if scanned_names and scanned_names == rec_ing_names:
                existing_ai_recipe = rec
                break

        # If not generated yet for this exact ingredient set, generate & save a brand new AI recipe into SQLite DB!
        if not existing_ai_recipe:
            generated_recipe = recipe_service.generate_and_save_ai_recipe(
                db,
                user_ingredients=req.ingredients,
                prompt_hint="Create an exciting, healthy new custom recipe featuring these exact user ingredients."
            )

    results = recipe_service.find_recipes(
        db,
        user_ingredients=req.ingredients,
        filters=req.filters,
        include_pantry=req.include_pantry
    )

    if generated_recipe:
        generated_id = generated_recipe["id"]
        # Pin the newly generated AI recipe to the very top!
        results.sort(key=lambda recipe: recipe["id"] != generated_id)

    return {
        "count": len(results),
        "recipes": results,
        "ai_recipe_generated": generated_recipe is not None or len([r for r in results if r['id'].startswith('ai-recipe-')]) > 0,
        "generated_recipe_id": generated_recipe["id"] if generated_recipe else (results[0]["id"] if results else None),
        "new_ingredients": unknown_names,
    }



@router.get("/{recipe_id}")
def get_recipe(
    recipe_id: str,
    servings: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    details = recipe_service.get_recipe_details(db, recipe_id=recipe_id, servings=servings)
    if not details:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return details

@router.post("/{recipe_id}/improve")
def improve_meal(recipe_id: str, req: ImproveMealRequest, db: Session = Depends(get_db)):
    """
    Improves recipe health profile by optimizing oil/fat, adding fresh veggies, or swapping ingredients.
    Returns comparison between original and improved macro values.
    """
    recipe_data = recipe_service.get_recipe_details(db, recipe_id=recipe_id, servings=req.servings)
    if not recipe_data:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    servings = req.servings or recipe_data["servings"]
    original_nutrition = recipe_data["per_serving_nutrition"]
    original_health = recipe_data["health_score"]

    # Clone ingredient table
    modified_ingredients = []
    applied_changes = []

    for item in recipe_data["ingredient_table"]:
        ing_name = item["ingredient"].lower()
        qty = item["required_quantity"]
        unit = item["unit"]

        # 1. Option: Reduce oil / fat by half
        if req.reduce_oil and ing_name in ["oil", "butter"]:
            new_qty = max(2.0, round(qty * 0.5, 1))
            applied_changes.append(f"Reduced {item['ingredient']} from {qty}{unit} to {new_qty}{unit} (-50% fat)")
            qty = new_qty

        # 2. Option: Substitutions
        if req.substitutions and ing_name in req.substitutions:
            sub_to = req.substitutions[ing_name]
            applied_changes.append(f"Substituted {item['ingredient']} with {sub_to.capitalize()}")
            ing_name = sub_to.lower()

        modified_ingredients.append({
            "ingredient": ing_name,
            "quantity": qty,
            "unit": unit
        })

    # 3. Option: Add green veggies if requested
    if req.add_veggies:
        modified_ingredients.append({
            "ingredient": "spinach",
            "quantity": 100 * (servings / 2.0),
            "unit": "g"
        })
        applied_changes.append("Added 100g fresh spinach (+2.2g fiber, rich in iron & vitamins)")

    # 4. Option: Boost protein
    if req.boost_protein:
        modified_ingredients.append({
            "ingredient": "chickpeas",
            "quantity": 80 * (servings / 2.0),
            "unit": "g"
        })
        applied_changes.append("Added 80g boiled chickpeas (+7g clean protein)")

    # Recalculate nutrition
    improved_nutr = nutrition_service.calculate_recipe_nutrition(db, modified_ingredients, servings=servings)
    improved_per_serving = improved_nutr["per_serving"]
    improved_health = scoring_service.calculate_health_score(improved_per_serving)

    # Calculate percentage improvements
    cal_diff_pct = round(((improved_per_serving["calories"] - original_nutrition["calories"]) / original_nutrition["calories"]) * 100, 1)
    protein_diff_pct = round(((improved_per_serving["protein"] - original_nutrition["protein"]) / max(1.0, original_nutrition["protein"])) * 100, 1)
    fiber_diff_pct = round(((improved_per_serving["fiber"] - original_nutrition["fiber"]) / max(0.5, original_nutrition["fiber"])) * 100, 1)

    # Generate AI Chef Tip
    ai_chef_tip = "These simple tweaks lower overall saturated fat and boost dietary fiber without compromising authentic flavor."

    return {
        "recipe_id": recipe_id,
        "servings": servings,
        "applied_changes": applied_changes,
        "changes_summary": f"Modified {len(applied_changes)} ingredient parameters to improve meal score.",
        "original_health_score": original_health,
        "improved_health_score": improved_health,
        "original_nutrition": original_nutrition,
        "improved_nutrition": improved_per_serving,
        "improvements": {
            "calories_pct": cal_diff_pct,
            "protein_pct": protein_diff_pct,
            "fiber_pct": fiber_diff_pct
        },
        "ai_chef_tip": ai_chef_tip
    }
