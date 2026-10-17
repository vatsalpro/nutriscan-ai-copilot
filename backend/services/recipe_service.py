import json
import logging
import time
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
        Finds and scores recipes based on scanned user ingredients and available pantry items.
        Prioritizes recipes that match the user's directly scanned/entered ingredients.
        """
        if filters is None:
            filters = {}

        scanned_set = set()
        available_set = set()
        use_soon_set = set()

        for item in user_ingredients or []:
            name = str(item.get("name") or item.get("ingredient") or "").lower().strip()
            if name:
                scanned_set.add(name)
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
        seen_names = set()

        # Sort so newest AI recipes come first before deduplication
        all_recipes.sort(key=lambda r: (0 if r.id.startswith("ai-recipe-") else 1, r.id), reverse=False)

        for rec in all_recipes:
            norm_title = (rec.name or "").strip().lower()
            if norm_title in seen_names:
                continue

            rec_ings = db.query(RecipeIngredientDB).filter(RecipeIngredientDB.recipe_id == rec.id).all()
            total_req = len(rec_ings)
            if total_req == 0:
                continue

            available_list = []
            missing_list = []
            matched_count = 0
            scanned_match_count = 0
            use_soon_matches = 0

            for req in rec_ings:
                req_name = req.ingredient.lower().strip()
                req_dict = {
                    "ingredient": req.ingredient,
                    "quantity": req.quantity,
                    "unit": req.unit
                }

                is_scanned_match = any(
                    req_name == s or s in req_name or req_name in s
                    for s in scanned_set
                ) if scanned_set else False

                is_available_match = is_scanned_match or any(
                    req_name == a or a in req_name or req_name in a
                    for a in available_set
                )

                if is_scanned_match:
                    scanned_match_count += 1

                if is_available_match:
                    matched_count += 1
                    available_list.append(req_dict)
                    if req_name in use_soon_set:
                        use_soon_matches += 1
                else:
                    missing_list.append(req_dict)

            raw_match_ratio = matched_count / total_req
            match_percentage = int(raw_match_ratio * 100)

            scanned_ratio = (scanned_match_count / len(scanned_set)) if scanned_set else 0.0
            boosted_score = (
                match_percentage
                + int(scanned_ratio * 100)
                + (scanned_match_count * 35)
                + (use_soon_matches * 5)
            )

            tags = json.loads(rec.tags_json) if rec.tags_json else []
            tags_lower = [str(t).lower().strip() for t in tags]
            total_time = rec.prep_time + rec.cook_time

            if filters.get("under_20") and total_time > 20:
                continue
            if filters.get("under_30") and total_time > 30:
                continue
            if filters.get("vegetarian") and "vegetarian" not in tags_lower and "vegan" not in tags_lower:
                continue
            if filters.get("vegan") and "vegan" not in tags_lower:
                continue

            nutr = nutrition_service.calculate_recipe_nutrition(
                db,
                [{"ingredient": r.ingredient, "quantity": r.quantity, "unit": r.unit} for r in rec_ings],
                servings=rec.servings
            )
            per_serving = nutr["per_serving"]

            cost_data = cost_service.calculate_recipe_cost(
                db,
                [{"ingredient": r.ingredient, "quantity": r.quantity, "unit": r.unit} for r in rec_ings],
                default_cost=rec.estimated_cost
            )
            total_cost = cost_data["estimated_cost_total"]

            if filters.get("budget") and total_cost > 120.0:
                continue
            max_budget = filters.get("max_budget")
            if max_budget and total_cost > float(max_budget):
                continue

            if filters.get("high_protein") and per_serving["protein"] < 18.0 and "high protein" not in tags_lower:
                continue
            if filters.get("low_calorie") and per_serving["calories"] > 450.0:
                continue
            if filters.get("high_fiber") and per_serving["fiber"] < 5.0:
                continue

            health_score_data = scoring_service.calculate_health_score(per_serving)
            seen_names.add(norm_title)

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
                "estimated_cost": total_cost,
                "cost_per_serving": round(total_cost / max(1, rec.servings), 1),
                "match_percentage": match_percentage,
                "boosted_score": boosted_score,
                "scanned_match_count": scanned_match_count,
                "available_count": matched_count,
                "total_required": total_req,
                "match_summary": f"{matched_count} of {total_req} ingredients available",
                "use_soon_match_count": use_soon_matches,
                "available_ingredients": available_list,
                "missing_ingredients": missing_list,
                "per_serving_nutrition": per_serving,
                "health_score": health_score_data
            })

        results.sort(
            key=lambda x: (
                1 if x["scanned_match_count"] > 0 else 0,
                x["boosted_score"],
                x["match_percentage"]
            ),
            reverse=True
        )
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
            is_available = any(
                req_name == a or a in req_name or req_name in a
                for a in available_set if a
            )
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
        Uses the sequential three-provider AI failover stack (OpenRouter -> Groq -> Gemini)
        to invent a custom recipe centered on the user's scanned ingredients,
        saves it to SQLite, and returns the full recipe details object.
        """
        ing_items = []
        for i in user_ingredients or []:
            name = str(i.get("name") or i.get("ingredient") or "").strip().lower()
            if name:
                qty = float(i.get("estimated_quantity") or i.get("quantity") or 100)
                unit = str(i.get("unit") or "g")
                ing_items.append({"ingredient": name, "quantity": qty, "unit": unit})

        if not ing_items:
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

        generated_data = None
        try:
            if ai_router.active:
                recipe_prompt = f"""Create ONE delicious, practical home-cooked recipe centered around these exact user ingredients: [{ing_str}].{hint_text}

Requirements:
1. Every ingredient in [{ing_str}] MUST be used in the "ingredients" list.
2. Do NOT add unrelated main ingredients. You may only add 1-2 basic seasonings (like salt, black pepper, olive oil, or honey/lemon if appropriate).
3. Keep prep_time + cook_time under 20 minutes if possible.
4. Return ONLY valid, compact JSON matching this exact schema (no markdown, no extra commentary):
{{
  "name": "Creative recipe title featuring {primary_name.title()}",
  "description": "One sentence appetizing description.",
  "prep_time": 8,
  "cook_time": 10,
  "servings": 2,
  "difficulty": "Easy",
  "estimated_cost": 95.0,
  "tags": ["AI Created", "Healthy", "Vegetarian", "Under 20 min"],
  "ingredients": [
    {{"ingredient": "{primary_name}", "quantity": 150, "unit": "g"}}
  ],
  "steps": [
    "Step 1 instruction.",
    "Step 2 instruction.",
    "Step 3 instruction."
  ],
  "substitutions": []
}}"""

                def _validate_recipe(data: Any) -> bool:
                    return (
                        isinstance(data, dict)
                        and isinstance(data.get("name"), str)
                        and bool(data["name"].strip())
                        and isinstance(data.get("ingredients"), list)
                        and len(data["ingredients"]) > 0
                        and isinstance(data.get("steps"), list)
                        and len(data["steps"]) > 0
                    )

                result = ai_router.json_text(
                    recipe_prompt,
                    system="You are NutriScan's culinary chef AI. Output strictly valid JSON only.",
                    max_tokens=600,
                    validator=_validate_recipe,
                )
                generated_data = result["json"]
                logger.info("AI recipe generated by %s/%s", result["provider"], result["model"])
        except Exception as exc:
            logger.warning("All AI recipe providers failed: %s", ai_router._sanitize_error(exc))

        if not generated_data or "name" not in generated_data:
            recipe_title = f"Chef AI {primary_name.title()}"
            if secondary_name:
                recipe_title += f" & {secondary_name.title()} Bowl"
            else:
                recipe_title += " Fresh Medley"

            fallback_ingredients = [
                {
                    "ingredient": item["ingredient"],
                    "quantity": item["quantity"],
                    "unit": item["unit"]
                }
                for item in ing_items
            ]
            if not fallback_ingredients:
                fallback_ingredients = [{"ingredient": primary_name, "quantity": 200, "unit": "g"}]

            generated_data = {
                "name": recipe_title,
                "description": f"A fresh, balanced custom recipe crafted around your {ing_str}.",
                "prep_time": 8,
                "cook_time": 10,
                "servings": 2,
                "difficulty": "Easy",
                "estimated_cost": 95.0,
                "tags": ["AI Created", "Healthy", "Vegetarian", "Under 20 min"],
                "ingredients": fallback_ingredients,
                "steps": [
                    f"Prepare and portion the {ing_str} into bite-sized pieces.",
                    f"Combine {primary_name} in a pan or bowl over gentle heat for 5-8 minutes.",
                    f"Fold in {secondary_name if secondary_name else 'seasonings'} until aromatic and well combined.",
                    "Plate warm and enjoy your fresh, nutrient-rich dish!"
                ],
                "substitutions": []
            }

        gen_ings = generated_data.get("ingredients") or []
        existing_gen_names = {
            str(x.get("ingredient") or x.get("name") or "").lower().strip()
            for x in gen_ings if isinstance(x, dict)
        }
        for user_item in ing_items:
            u_name = user_item["ingredient"]
            if not any(u_name == g or u_name in g or g in u_name for g in existing_gen_names if g):
                gen_ings.append(user_item)
        generated_data["ingredients"] = gen_ings

        recipe_id = f"ai-recipe-{time.time_ns()}"
        tags = generated_data.get("tags", ["AI Created", "Healthy", "Vegetarian"])
        if not isinstance(tags, list):
            tags = ["AI Created", "Healthy"]
        if "AI Created" not in tags:
            tags.insert(0, "AI Created")

        img_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
        if "chicken" in primary_name:
            img_url = "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=800&q=80"
        elif "egg" in primary_name:
            img_url = "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=800&q=80"
        elif "paneer" in primary_name or "cheese" in primary_name:
            img_url = "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=800&q=80"
        elif "rice" in primary_name:
            img_url = "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=800&q=80"
        elif "fish" in primary_name or "salmon" in primary_name or "prawn" in primary_name:
            img_url = "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=800&q=80"
        elif any(f in primary_name for f in ("apple", "banana", "berry", "strawberry", "mango", "dragonfruit", "oats")):
            img_url = "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=800&q=80"

        new_rec = RecipeDB(
            id=recipe_id,
            name=generated_data.get("name", f"AI {primary_name.title()} Recipe"),
            description=generated_data.get("description", "A custom recipe generated by NutriScan AI."),
            prep_time=int(generated_data.get("prep_time", 8)),
            cook_time=int(generated_data.get("cook_time", 10)),
            servings=max(1, int(generated_data.get("servings", 2))),
            difficulty=generated_data.get("difficulty", "Easy"),
            image_url=img_url,
            tags_json=json.dumps(tags),
            estimated_cost=float(generated_data.get("estimated_cost", 95.0)),
            steps_json=json.dumps(generated_data.get("steps", [])),
            substitutions_json=json.dumps(generated_data.get("substitutions", [])),
            improvements_json=json.dumps([])
        )
        db.add(new_rec)
        db.commit()

        for ing_item in generated_data.get("ingredients", []):
            ing_name = str(ing_item.get("ingredient") or ing_item.get("name") or "").lower().strip()
            if not ing_name:
                continue
            try:
                qty_val = float(ing_item.get("quantity") or ing_item.get("estimated_quantity") or 100)
            except (TypeError, ValueError):
                qty_val = 100.0
            rec_ing = RecipeIngredientDB(
                recipe_id=recipe_id,
                ingredient=ing_name,
                quantity=qty_val,
                unit=str(ing_item.get("unit") or "g")
            )
            db.add(rec_ing)
        db.commit()

        return RecipeService.get_recipe_details(db, recipe_id=recipe_id, user_ingredients=user_ingredients)


recipe_service = RecipeService()
