import logging
from typing import Any

from services.ai_router import ai_router, AIRequestValidationError
from services.demo_provider import DemoVisionProvider

logger = logging.getLogger(__name__)


def _validate_ingredients_payload(data: Any) -> bool:
    if isinstance(data, list) and len(data) > 0:
        # Some models return a raw JSON array; cannot mutate type in-place, so require dict wrapper
        return False
    if not isinstance(data, dict):
        return False
    ingredients = data.get("ingredients") or data.get("items") or data.get("detected_ingredients")
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        return False

    normalized = []
    for item in ingredients:
        if isinstance(item, str) and item.strip():
            normalized.append({
                "name": item.strip().lower(),
                "estimated_quantity": 100,
                "unit": "g",
                "confidence": 0.9,
            })
        elif isinstance(item, dict):
            raw_name = (
                item.get("name")
                or item.get("ingredient")
                or item.get("item")
                or item.get("food")
            )
            if not isinstance(raw_name, str) or not raw_name.strip():
                continue
            qty = item.get("estimated_quantity")
            if qty is None:
                qty = item.get("quantity", 100)
            try:
                qty = float(qty) if qty is not None else 100
            except (ValueError, TypeError):
                qty = 100
            unit = str(item.get("unit") or "g").strip() or "g"
            conf = item.get("confidence", 0.9)
            try:
                conf = float(conf)
                if conf > 1.0:
                    conf = round(conf / 100.0, 2)
            except (ValueError, TypeError):
                conf = 0.9
            normalized.append({
                "name": raw_name.strip().lower(),
                "estimated_quantity": qty,
                "unit": unit,
                "confidence": conf,
            })

    if not normalized:
        return False
    data["ingredients"] = normalized
    return True


def _validate_meal_payload(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    meal = data.get("meal")
    if not isinstance(meal, dict):
        if "meal_name" in data or "dish" in data or "name" in data:
            meal = dict(data)
            data["meal"] = meal
        else:
            return False

    meal_name = meal.get("meal_name") or meal.get("dish") or meal.get("name")
    if not isinstance(meal_name, str) or not meal_name.strip():
        return False
    meal["meal_name"] = meal_name.strip()

    nutrition = meal.get("nutrition")
    if not isinstance(nutrition, dict):
        if "calories" in meal or "calories_kcal" in meal:
            nutrition = {
                "calories": meal.get("calories") or meal.get("calories_kcal") or 350,
                "protein": meal.get("protein") or meal.get("protein_g") or 15,
                "carbs": meal.get("carbs") or meal.get("carbs_g") or 40,
                "fat": meal.get("fat") or meal.get("fat_g") or 12,
                "fiber": meal.get("fiber") or meal.get("fiber_g") or 4,
            }
            meal["nutrition"] = nutrition
        else:
            return False

    if "calories" not in nutrition:
        if "calories_kcal" in nutrition:
            nutrition["calories"] = nutrition["calories_kcal"]
        else:
            return False

    meal.setdefault("estimated_portion", meal.get("serving_size") or "~300g")
    meal.setdefault("confidence", 0.92)
    meal.setdefault("portion_confidence", 0.80)
    meal.setdefault("description", f"Vision AI nutrition estimate for {meal['meal_name']}.")
    return True


class VisionService:
    def __init__(self):
        self.demo_provider = DemoVisionProvider()

    async def scan_ingredients(self, image_bytes: bytes, filename: str = "", mime_type: str = "image/jpeg") -> dict:
        prompt = """Analyze this kitchen/food image for NutriScan.

Identify EVERY clearly visible edible food ingredient. This is an open-world task:
do not restrict the answer to a predefined ingredient list.

Rules:
- Identify all visible food items, fruits, vegetables, proteins, grains, spices, or packaged foods.
- Normalize each ingredient to a simple lowercase name.
- Estimate quantity (numeric value, e.g. 2 or 150).
- Use units such as g, ml, pcs, tsp, tbsp, cloves.
- Give confidence from 0.0 to 1.0.
- Return ONLY valid JSON matching the exact schema below.

Schema:
{
  "ingredients": [
    {
      "name": "apple",
      "estimated_quantity": 2,
      "unit": "pcs",
      "confidence": 0.97
    }
  ]
}"""
        try:
            result = ai_router.json_image(
                image_bytes=image_bytes,
                mime_type=mime_type,
                prompt=prompt,
                max_tokens=1000,
                validator=_validate_ingredients_payload,
            )
            data = result["json"]
            return {
                "provider": f'{result["provider"]} ({result["model"]})',
                "is_demo": False,
                "ingredients": data.get("ingredients", []),
            }
        except AIRequestValidationError:
            raise
        except Exception as exc:
            sanitized_exc = ai_router._sanitize_error(exc)
            logger.warning("All AI ingredient providers failed: %s", sanitized_exc)
            result = await self.demo_provider.analyze_ingredients(image_bytes, filename)
            result["is_demo"] = True
            result["fallback_reason"] = sanitized_exc
            return result

    async def scan_meal(self, image_bytes: bytes, filename: str = "", mime_type: str = "image/jpeg") -> dict:
        prompt = """Analyze this prepared cooked meal image for NutriScan.
Identify the dish, estimate visible portion, and estimate nutrition.
These are rough estimates, not medical measurements.

Return ONLY valid JSON:
{
  "meal": {
    "meal_name": "Chicken Biryani",
    "estimated_portion": "~350g",
    "confidence": 0.92,
    "portion_confidence": 0.70,
    "nutrition": {
      "calories": 620,
      "protein": 28,
      "carbs": 72,
      "fat": 24,
      "fiber": 4
    },
    "description": "Short dish description"
  }
}"""
        try:
            result = ai_router.json_image(
                image_bytes=image_bytes,
                mime_type=mime_type,
                prompt=prompt,
                max_tokens=850,
                validator=_validate_meal_payload,
            )
            data = result["json"]
            return {
                "provider": f'{result["provider"]} ({result["model"]})',
                "is_demo": False,
                "meal": data.get("meal", {}),
            }
        except AIRequestValidationError:
            raise
        except Exception as exc:
            sanitized_exc = ai_router._sanitize_error(exc)
            logger.warning("All AI meal providers failed: %s", sanitized_exc)
            result = await self.demo_provider.analyze_meal(image_bytes, filename)
            result["is_demo"] = True
            result["fallback_reason"] = sanitized_exc
            return result


vision_service = VisionService()
