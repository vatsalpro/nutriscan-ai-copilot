import logging
from typing import Any

from services.ai_router import ai_router, AIRequestValidationError
from services.demo_provider import DemoVisionProvider

logger = logging.getLogger(__name__)


def _validate_ingredients_payload(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    ingredients = data.get("ingredients")
    if not isinstance(ingredients, list) or len(ingredients) == 0:
        return False
    for item in ingredients:
        if not isinstance(item, dict):
            return False
        name = item.get("name") or item.get("ingredient")
        if not isinstance(name, str) or not name.strip():
            return False
    return True


def _validate_meal_payload(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    meal = data.get("meal")
    if not isinstance(meal, dict):
        return False
    meal_name = meal.get("meal_name")
    nutrition = meal.get("nutrition")
    if not isinstance(meal_name, str) or not meal_name.strip():
        return False
    if not isinstance(nutrition, dict) or "calories" not in nutrition:
        return False
    return True


class VisionService:
    def __init__(self):
        self.demo_provider = DemoVisionProvider()

    async def scan_ingredients(self, image_bytes: bytes, filename: str = "", mime_type: str = "image/jpeg") -> dict:
        prompt = """Analyze this kitchen/food image for NutriScan.

Identify EVERY clearly visible edible food ingredient. This is an open-world task:
do not restrict the answer to a predefined ingredient list.

Rules:
- Do not invent ingredients that are not visible.
- Normalize each ingredient to a simple lowercase name.
- Estimate quantity only when visually reasonable; otherwise use null.
- Use units such as g, ml, pcs, tsp, tbsp, cloves.
- Give confidence from 0.0 to 1.0.
- Return ONLY valid JSON.

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
