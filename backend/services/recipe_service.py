import json
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database.models import RecipeDB, RecipeIngredientDB, PantryItem
from services.nutrition_service import nutrition_service
from services.scoring_service import scoring_service
from services.cost_service import cost_service
from services.ai_router import ai_router

logger = logging.getLogger(__name__)

class RecipeService:
    @staticmethod
    def find_recipes(
        db: Session,
        user_ingredients: List[Dict[str, Any]],
        filters: Dict[str, Any] = None,
        include_pantry: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Finds and scores recipes based on available ingredients.
        """
        if filters is None:
            filters = {}

        # Collect normalized user ingredient names
        available_set = set()
        use_soon_set = set()

        for item in user_ingredients:
            name = str(item.get("name") or item.get("ingredient") or "").lower().strip()
            if name:
                available_set.add(name)

        if include_pantry:
            pantry_items = db.query(PantryItem).all()
            for p in pantry_items:
                p_name = p.ingredient.lower().strip()
                available_set.add(p_name)
                if p.freshness in ["Use Soon", "Expiring Soon"]:
                    use_soon_set.add(p_name)

        all_recipes = db.query(RecipeDB).all()
        results = []

        for rec in all_recipes:
            rec_ings = db.query(RecipeIngredientDB).filter(RecipeIngredientDB.recipe_id == rec.id).all()
            total_req = len(rec_ings)
            if total_req == 0:
                continue

            available_list = []
            missing_list = []
            matched_count = 0
            use_soon_matches = 0

            for req in rec_ings:
                req_name = req.ingredient.lower().strip()
                req_dict = {
                    "ingredient": req.ingredient,
                    "quantity": req.quantity,
                    "unit": req.unit
                }

                if req_name in available_set:
                    matched_count += 1
                    available_list.append(req_dict)
                    if req_name in use_soon_set:
                        use_soon_matches += 1
                else:
                    missing_list.append(req_dict)

            # Match Percentage Calculation
            raw_match_ratio = matched_count / total_req
            match_percentage = int(raw_match_ratio * 100)

            # Boost priority if uses expiring/use-soon ingredients
            boosted_score = match_percentage + (use_soon_matches * 5)

            # Check Filters
            tags = json.loads(rec.tags_json) if rec.tags_json else []
            total_time = rec.prep_time + rec.cook_time

            # Filter: Under 20 mins
            if filters.get("under_20") and total_time > 20:
                continue
            # Filter: Under 30 mins
            if filters.get("under_30") and total_time > 30:
                continue
            # Filter: Vegetarian
            if filters.get("vegetarian") and "vegetarian" not in tags and "vegan" not in tags:
                continue
            # Filter: Vegan
            if filters.get("vegan") and "vegan" not in tags:
                continue
            # Filter: Budget max
            max_budget = filters.get("max_budget")
            if max_budget and rec.estimated_cost > float(max_budget):
                continue

            # Calculate Nutrition
            nutr = nutrition_service.calculate_recipe_nutrition(
                db, 
                [{"ingredient": r.ingredient, "quantity": r.quantity, "unit": r.unit} for r in rec_ings],
                servings=rec.servings
            )
            per_serving = nutr["per_serving"]

            # Filter: High Protein (>20g)
            if filters.get("high_protein") and per_serving["protein"] < 20.0:
                continue
            # Filter: Low Calorie (<450 kcal)
            if filters.get("low_calorie") and per_serving["calories"] > 450.0:
                continue
            # Filter: High Fiber (>5g)
            if filters.get("high_fiber") and per_serving["fiber"] < 5.0:
                continue

            health_score_data = scoring_service.calculate_health_score(per_serving)
            cost_data = cost_service.calculate_recipe_cost(
                db, 
                [{"ingredient": r.ingredient, "quantity": r.quantity, "unit": r.unit} for r in rec_ings],
                default_cost=rec.estimated_cost
            )

            results.append({
                "id": rec.id,
                "name": rec.name,
                "description": rec.description,
                "prep_time": rec.prep_time,
                "cook_time": rec.cook_time,
                "total_time": total_time,
                "servings": rec.servings,
                "difficulty": rec.difficulty,
                "image_url": rec.image_url,
                "tags": tags,
                "estimated_cost": cost_data["estimated_cost_total"],
                "cost_per_serving": round(cost_data["estimated_cost_total"] / rec.servings, 1),
                "match_percentage": match_percentage,
                "boosted_score": boosted_score,
                "available_count": matched_count,
                "total_required": total_req,
                "match_summary": f"{matched_count} of {total_req} ingredients available",
                "use_soon_match_count": use_soon_matches,
                "available_ingredients": available_list,
                "missing_ingredients": missing_list,
                "per_serving_nutrition": per_serving,
                "health_score": health_score_data
            })

        # Sort by boosted score desc, then match_percentage desc
        results.sort(key=lambda x: (x["boosted_score"], x["match_percentage"]), reverse=True)
        return results

    @staticmethod
    def get_recipe_details(db: Session, recipe_id: str, user_ingredients: List[Dict[str, Any]] = None, servings: int = None) -> Dict[str, Any]:
        rec = db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not rec:
            return None

        if user_ingredients is None:
            user_ingredients = []

        available_set = set(str(i.get("name") or i.get("ingredient") or "").lower().strip() for i in user_ingredients)
        pantry_items = db.query(PantryItem).all()
        for p in pantry_items:
            available_set.add(p.ingredient.lower().strip())

        rec_ings = db.query(RecipeIngredientDB).filter(RecipeIngredientDB.recipe_id == rec.id).all()
        
        target_servings = servings if (servings and servings > 0) else rec.servings
        scaling_ratio = target_servings / float(rec.servings)

        ingredient_table = []
        available_count = 0

        scaled_ing_list_for_nutr = []

        for req in rec_ings:
            req_name = req.ingredient.lower().strip()
            scaled_qty = round(req.quantity * scaling_ratio, 1)
            is_available = req_name in available_set
            if is_available:
                available_count += 1

            ingredient_table.append({
                "ingredient": req.ingredient,
                "required_quantity": scaled_qty,
                "unit": req.unit,
                "is_available": is_available,
                "available_status": f"✓ {scaled_qty}{req.unit}" if is_available else "❌ Missing"
            })

            scaled_ing_list_for_nutr.append({
                "ingredient": req.ingredient,
                "quantity": scaled_qty,
                "unit": req.unit
            })

        match_pct = int((available_count / len(rec_ings)) * 100) if rec_ings else 0

        nutr = nutrition_service.calculate_recipe_nutrition(db, scaled_ing_list_for_nutr, servings=target_servings)
        health_score_data = scoring_service.calculate_health_score(nutr["per_serving"])
        cost_data = cost_service.calculate_recipe_cost(db, scaled_ing_list_for_nutr, default_cost=rec.estimated_cost * scaling_ratio)

        return {
            "id": rec.id,
            "name": rec.name,
            "description": rec.description,
            "prep_time": rec.prep_time,
            "cook_time": rec.cook_time,
            "total_time": rec.prep_time + rec.cook_time,
            "servings": target_servings,
            "original_servings": rec.servings,
            "difficulty": rec.difficulty,
            "image_url": rec.image_url,
            "tags": json.loads(rec.tags_json) if rec.tags_json else [],
            "steps": json.loads(rec.steps_json) if rec.steps_json else [],
            "substitutions": json.loads(rec.substitutions_json) if rec.substitutions_json else [],
            "improvements": json.loads(rec.improvements_json) if rec.improvements_json else [],
            "ingredient_table": ingredient_table,
            "match_percentage": match_pct,
            "available_count": available_count,
            "total_required": len(rec_ings),
            "match_summary": f"You have {available_count} of {len(rec_ings)} required ingredients ({match_pct}% match).",
            "estimated_cost": cost_data["estimated_cost_total"],
            "cost_per_serving": round(cost_data["estimated_cost_total"] / target_servings, 1),
            "per_serving_nutrition": nutr["per_serving"],
            "total_nutrition": nutr["total_recipe"],
            "health_score": health_score_data
        }

    @staticmethod
    def generate_and_save_ai_recipe(db: Session, user_ingredients: List[Dict[str, Any]], prompt_hint: str = None) -> Dict[str, Any]:
        """
        Uses a three-provider AI failover stack to invent a brand new custom recipe based on user's available ingredients,
        saves it permanently to the SQLite database (recipes and recipe_ingredients tables),
        and returns the full recipe details object.
        """
        import time, json
        from config import settings

        ing_items = []
        for i in user_ingredients:
            name = str(i.get("name") or i.get("ingredient") or "").strip().lower()
            if name:
                qty = float(i.get("estimated_quantity") or i.get("quantity") or 100)
                unit = str(i.get("unit") or "g")
                ing_items.append({"ingredient": name, "quantity": qty, "unit": unit})

        pantry_items = db.query(PantryItem).all()
        for p in pantry_items:
            p_name = p.ingredient.lower().strip()
            if p_name not in [x["ingredient"] for x in ing_items]:
                ing_items.append({"ingredient": p_name, "quantity": 100, "unit": "g"})

        ing_names_list = [x["ingredient"] for x in ing_items]
        ing_str = ", ".join(ing_names_list) if ing_names_list else "paneer, tomato, onion, capsicum, spinach"
        primary_name = ing_names_list[0] if ing_names_list else "vegetables"
        secondary_name = ing_names_list[1] if len(ing_names_list) > 1 else ""

        hint_text = f" User flavor/style request: '{prompt_hint}'" if prompt_hint else ""

        system_prompt = f"""You are a Master Culinary Chef AI.
Invent a completely unique, delicious, authentic, and healthy recipe using these available ingredients: [{ing_str}].{hint_text}
Requirements:
1. You MUST include these key ingredients [{ing_str}] in the recipe.
2. Provide step-by-step cooking instructions.
3. Make it genuinely healthy: favor vegetables, lean protein, fibre, and modest oil.

Return ONLY a valid JSON object matching this schema exactly:
{{
  "name": "Chef AI Spiced {primary_name.title()} & {secondary_name.title() if secondary_name else 'Veggies'} Medley",
  "description": "A vibrant, aromatic dish featuring fresh {primary_name} cooked with wholesome ingredients and authentic spices.",
  "prep_time": 10,
  "cook_time": 15,
  "servings": 2,
  "difficulty": "Easy",
  "estimated_cost": 120.0,
  "tags": ["AI Created", "Healthy", "Custom Recipe", "High Protein"],
  "ingredients": [
    {{"ingredient": "{primary_name}", "quantity": 200, "unit": "g"}}
  ],
  "steps": [
    "Prepare all ingredients into bite-sized pieces.",
    "Heat oil in a heavy skillet over medium-high heat.",
    "Add main ingredients and cook until tender and fragrant.",
    "Season lightly with salt, pepper, and serve hot."
  ],
  "substitutions": []
}}"""

        generated_data = None
        try:
            if ai_router.active:
                recipe_prompt = f"""Create ONE genuinely useful recipe using these available ingredients:
[{ing_str}].
{hint_text}

Requirements:
1. Prefer ingredients the user already has.
2. You may add a small number of common pantry staples such as salt, pepper, oil, water or basic spices.
3. Give realistic quantities and step-by-step instructions.
4. Make it practical for a home kitchen.
5. Return ONLY valid JSON.

Schema:
{{
  "name": "Creative recipe name",
  "description": "Short description",
  "prep_time": 10,
  "cook_time": 15,
  "servings": 2,
  "difficulty": "Easy",
  "estimated_cost": 120.0,
  "tags": ["AI Created", "Healthy"],
  "ingredients": [
    {{"ingredient": "ingredient name", "quantity": 100, "unit": "g"}}
  ],
  "steps": ["Step 1", "Step 2"],
  "substitutions": []
}}"""
                result = ai_router.json_text(
                    recipe_prompt,
                    system="You are NutriScan's expert AI recipe generator. Generate safe, practical culinary recipes.",
                    max_tokens=1400,
                )
                generated_data = result["json"]
                logger.info("AI recipe generated by %s/%s", result["provider"], result["model"])
        except Exception as exc:
            logger.warning("All AI recipe providers failed: %s", exc)

        if not generated_data or "name" not in generated_data:
            recipe_title = f"Chef AI {primary_name.title()}"
            if secondary_name:
                recipe_title += f" & {secondary_name.title()} Medley"
            else:
                recipe_title += " Special Skillet"

            fallback_ingredients = []
            for item in ing_items:
                fallback_ingredients.append({
                    "ingredient": item["ingredient"],
                    "quantity": item["quantity"],
                    "unit": item["unit"]
                })

            if not fallback_ingredients:
                fallback_ingredients = [{"ingredient": primary_name, "quantity": 200, "unit": "g"}]

            generated_data = {
                "name": recipe_title,
                "description": f"A fresh, balanced custom recipe crafted by NutriScan AI using your scanned {ing_str}.",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 2,
                "difficulty": "Easy",
                "estimated_cost": 120.0,
                "tags": ["AI Created", "Healthy", "Balanced", "Quick & Easy"],
                "ingredients": fallback_ingredients,
                "steps": [
                    f"Wash and chop the {ing_str} into bite-sized pieces.",
                    "Heat 1 tbsp oil in a skillet over medium heat.",
                    f"Add {primary_name} and sear until golden and fragrant (4-5 mins).",
                    f"Incorporate {secondary_name if secondary_name else 'the remaining ingredients'} and stir-fry until tender.",
                    "Season with salt, black pepper, and serve hot immediately!"
                ],
                "substitutions": []
            }

        recipe_id = f"ai-recipe-{time.time_ns()}"
        tags = generated_data.get("tags", ["AI Created"])
        if "AI Created" not in tags:
            tags.insert(0, "AI Created")

        # Pick appropriate food image based on primary ingredient
        img_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
        if "chicken" in primary_name:
            img_url = "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80"
        elif "egg" in primary_name:
            img_url = "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80"
        elif "paneer" in primary_name or "cheese" in primary_name:
            img_url = "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=800&q=80"
        elif "rice" in primary_name:
            img_url = "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80"
        elif "fish" in primary_name or "prawn" in primary_name:
            img_url = "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80"

        new_rec = RecipeDB(
            id=recipe_id,
            name=generated_data.get("name", f"AI {primary_name.title()} Recipe"),
            description=generated_data.get("description", "A custom recipe generated by NutriScan AI."),
            prep_time=int(generated_data.get("prep_time", 10)),
            cook_time=int(generated_data.get("cook_time", 15)),
            servings=int(generated_data.get("servings", 2)),
            difficulty=generated_data.get("difficulty", "Easy"),
            image_url=img_url,
            tags_json=json.dumps(tags),
            estimated_cost=float(generated_data.get("estimated_cost", 120.0)),
            steps_json=json.dumps(generated_data.get("steps", [])),
            substitutions_json=json.dumps(generated_data.get("substitutions", [])),
            improvements_json=json.dumps([])
        )
        db.add(new_rec)
        db.commit()

        for ing_item in generated_data.get("ingredients", []):
            rec_ing = RecipeIngredientDB(
                recipe_id=recipe_id,
                ingredient=str(ing_item.get("ingredient") or ing_item.get("name") or "").lower().strip(),
                quantity=float(ing_item.get("quantity") or ing_item.get("estimated_quantity") or 100),
                unit=str(ing_item.get("unit") or "g")
            )
            db.add(rec_ing)
        db.commit()

        return RecipeService.get_recipe_details(db, recipe_id=recipe_id, user_ingredients=user_ingredients)

recipe_service = RecipeService()

