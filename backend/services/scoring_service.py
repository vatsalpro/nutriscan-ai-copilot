class ScoringService:
    @staticmethod
    def calculate_health_score(per_serving_nutrition: dict) -> dict:
        """
        Calculates NutriScore — General meal balance (0 to 100) based on macronutrient ratios.
        Note: This is a general nutritional balance score, not a medical measurement.
        """
        calories = per_serving_nutrition.get("calories", 400.0)
        protein = per_serving_nutrition.get("protein", 15.0)
        carbs = per_serving_nutrition.get("carbs", 30.0)
        fat = per_serving_nutrition.get("fat", 15.0)
        fiber = per_serving_nutrition.get("fiber", 4.0)

        # 1. Protein score (aim ~25g per serving for 100 pts)
        protein_score = min(100, int((protein / 25.0) * 100))

        # 2. Fiber score (aim ~8g per serving for 100 pts)
        fiber_score = min(100, int((fiber / 8.0) * 100))

        # 3. Vegetable / Micronutrient proxy score
        veggie_score = min(100, int(((fiber * 10.0 + protein * 2.0) / 70.0) * 100))

        # 4. Calorie density score (optimal range 350-550 kcal per main meal)
        if 300 <= calories <= 550:
            cal_score = 90
        elif calories < 300:
            cal_score = 75
        elif calories <= 700:
            cal_score = 70
        else:
            cal_score = 50

        # Weighted average
        overall = int(protein_score * 0.3 + fiber_score * 0.25 + veggie_score * 0.25 + cal_score * 0.2)
        overall = max(30, min(99, overall))

        return {
            "score": overall,
            "label": "NutriScore — General meal balance",
            "disclaimer": "NutriScore provides general meal balance estimates and is not a medical or dietary prescription.",
            "breakdown": {
                "protein_score": protein_score,
                "fiber_score": fiber_score,
                "veggie_score": veggie_score,
                "calorie_density_score": cal_score
            }
        }

scoring_service = ScoringService()
