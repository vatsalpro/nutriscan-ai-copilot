import random
import logging

logger = logging.getLogger(__name__)

class DemoVisionProvider:
    """
    Demo/Fallback Vision Provider when all configured AI providers are unavailable.
    Provides realistic ingredient detection for hackathon testing and offline demos.
    """
    
    DEMO_INGREDIENT_SETS = [
        # Hackathon primary demo scenario (Section 46)
        [
            {"name": "paneer", "estimated_quantity": 200, "unit": "g", "confidence": 0.94},
            {"name": "potato", "estimated_quantity": 250, "unit": "g", "confidence": 0.92},
            {"name": "tomato", "estimated_quantity": 150, "unit": "g", "confidence": 0.91},
            {"name": "onion", "estimated_quantity": 100, "unit": "g", "confidence": 0.89},
            {"name": "capsicum", "estimated_quantity": 80, "unit": "g", "confidence": 0.87}
        ],
        [
            {"name": "chicken", "estimated_quantity": 300, "unit": "g", "confidence": 0.95},
            {"name": "rice", "estimated_quantity": 250, "unit": "g", "confidence": 0.93},
            {"name": "capsicum", "estimated_quantity": 100, "unit": "g", "confidence": 0.88},
            {"name": "onion", "estimated_quantity": 80, "unit": "g", "confidence": 0.86}
        ],
        [
            {"name": "egg", "estimated_quantity": 4, "unit": "pcs", "confidence": 0.96},
            {"name": "bread", "estimated_quantity": 4, "unit": "pcs", "confidence": 0.94},
            {"name": "spinach", "estimated_quantity": 100, "unit": "g", "confidence": 0.88},
            {"name": "butter", "estimated_quantity": 20, "unit": "g", "confidence": 0.85}
        ]
    ]

    DEMO_MEAL_SETS = [
        {
            "meal_name": "Chicken Biryani",
            "estimated_portion": "~350g",
            "confidence": 0.94,
            "portion_confidence": 0.68,
            "nutrition": {
                "calories": 620,
                "protein": 28,
                "carbs": 72,
                "fat": 24,
                "fiber": 4
            },
            "description": "Rich Indian spiced rice dish cooked with marinated tender chicken piece."
        },
        {
            "meal_name": "Paneer Butter Masala & Naan",
            "estimated_portion": "~400g",
            "confidence": 0.92,
            "portion_confidence": 0.72,
            "nutrition": {
                "calories": 540,
                "protein": 22,
                "carbs": 58,
                "fat": 26,
                "fiber": 5
            },
            "description": "Creamy tomato-based cottage cheese curry served with wheat bread."
        }
    ]

    async def analyze_ingredients(self, image_bytes: bytes, filename: str = "") -> dict:
        logger.info(f"DemoVisionProvider analyzing ingredients for image: {filename}")
        # Select set based on image size or simple hash so same image yields consistent results
        idx = len(image_bytes) % len(self.DEMO_INGREDIENT_SETS)
        detected = self.DEMO_INGREDIENT_SETS[idx]
        return {
            "provider": "demo",
            "is_demo": True,
            "ingredients": detected,
            "message": "Processed using NutriScan Demo Vision Engine"
        }

    async def analyze_meal(self, image_bytes: bytes, filename: str = "") -> dict:
        logger.info(f"DemoVisionProvider analyzing meal for image: {filename}")
        idx = len(image_bytes) % len(self.DEMO_MEAL_SETS)
        meal = self.DEMO_MEAL_SETS[idx]
        return {
            "provider": "demo",
            "is_demo": True,
            "meal": meal,
            "message": "Processed using NutriScan Demo Meal Scanner"
        }
