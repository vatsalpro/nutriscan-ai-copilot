import sys
import os

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from database.database import SessionLocal
from database.models import RecipeDB, RecipeIngredientDB

client = TestClient(app)

def test_ai_recipe_generation_and_db_persistence():
    print("\n==========================================")
    print("  TESTING AI RECIPE GENERATION & DB PERSISTENCE")
    print("==========================================")

    # 1. Custom unique ingredients set
    test_ingredients = [
        {"name": "dragonfruit", "estimated_quantity": 150, "unit": "g"},
        {"name": "coconut milk", "estimated_quantity": 200, "unit": "ml"},
        {"name": "chia seeds", "estimated_quantity": 30, "unit": "g"}
    ]

    print(f"\n1. Submitting new ingredients: {[i['name'] for i in test_ingredients]}")
    
    response = client.post("/api/recipes/find", json={
        "ingredients": test_ingredients,
        "filters": {},
        "include_pantry": True
    })

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()

    print(f"   [OK] API Response Status: 200 OK")
    print(f"   [OK] ai_recipe_generated: {data.get('ai_recipe_generated')}")
    print(f"   [OK] Total recipes returned: {data.get('count')}")

    recipes = data.get("recipes", [])
    assert len(recipes) > 0, "No recipes returned!"

    top_recipe = recipes[0]
    generated_id = top_recipe["id"]
    print(f"   [OK] Top Recipe Name: '{top_recipe['name']}' (ID: {generated_id})")
    print(f"   [OK] Match Summary: {top_recipe['match_summary']}")

    # 2. Verify Database Persistence in SQLite nutriscan.db
    print("\n2. Verifying SQLite Database Persistence...")
    db = SessionLocal()
    try:
        db_recipe = db.query(RecipeDB).filter(RecipeDB.id == generated_id).first()
        assert db_recipe is not None, f"Recipe {generated_id} was NOT saved to SQLite database!"
        print(f"   [OK] Found RecipeDB record in SQLite: Name='{db_recipe.name}'")

        db_ingredients = db.query(RecipeIngredientDB).filter(RecipeIngredientDB.recipe_id == generated_id).all()
        ing_names = [r.ingredient for r in db_ingredients]
        print(f"   [OK] Found {len(db_ingredients)} RecipeIngredientDB records: {ing_names}")
    finally:
        db.close()

    # 3. Fetch Full Recipe Details Endpoint GET /api/recipes/{id}
    print(f"\n3. Fetching Full Recipe Details via GET /api/recipes/{generated_id}...")
    detail_res = client.get(f"/api/recipes/{generated_id}")
    assert detail_res.status_code == 200, "Recipe details lookup failed!"
    details = detail_res.json()

    print(f"   [OK] Recipe Title: {details['name']}")
    print(f"   [OK] Total Time: {details['total_time']} mins | Servings: {details['servings']}")
    print(f"   [OK] Number of Steps: {len(details['steps'])}")
    print(f"   [OK] Step 1: {details['steps'][0] if details['steps'] else 'N/A'}")
    print(f"   [OK] Per-serving Calories: {details['per_serving_nutrition']['calories']} kcal")


    print("\n==========================================")
    print("  AI RECIPE GENERATION & DB PERSISTENCE TEST PASSED! [OK]")
    print("==========================================")

if __name__ == "__main__":
    test_ai_recipe_generation_and_db_persistence()
