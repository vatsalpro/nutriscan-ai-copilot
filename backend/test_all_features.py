import os
import sys
import io
import json
from PIL import Image
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

client = TestClient(app)

IMG_INGREDIENTS = "test_ingredients.jpg"
IMG_MEAL = "test_meal.jpg"
IMG_BREAKFAST = "test_breakfast.jpg"

def get_test_image_bytes(color=(200, 100, 50)):
    buf = io.BytesIO()
    img = Image.new("RGB", (300, 300), color=color)
    img.save(buf, format="JPEG")
    return buf.getvalue()

def load_image_bytes(path, default_color=(200, 100, 50)):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return get_test_image_bytes(default_color)

def test_health():
    print("\n--- 1. Testing Root & Health Endpoints ---")
    r1 = client.get("/")
    assert r1.status_code == 200, f"Root failed: {r1.text}"
    print("Root response:", r1.json())
    
    r2 = client.get("/health")
    assert r2.status_code == 200, f"Health failed: {r2.text}"
    print("Health response:", r2.json())

def test_ingredient_scans():
    print("\n--- 2. Testing Ingredient Scans with Different Images & Formats ---")
    
    # Image 1: Ingredients JPEG
    jpg_bytes = load_image_bytes(IMG_INGREDIENTS, (220, 120, 60))
    
    res1 = client.post("/api/scan/ingredients", files={"file": ("ingredients.jpg", jpg_bytes, "image/jpeg")})
    assert res1.status_code == 200, f"JPG scan failed: {res1.text}"
    data1 = res1.json()
    print(f"Image 1 (JPG) Scan Result: Provider={data1.get('provider')}, Ingredients={len(data1.get('ingredients', []))}")
    for ing in data1.get("ingredients", []):
        print(f"  - {ing['name']}: {ing.get('estimated_quantity')} {ing.get('unit')} (conf: {ing.get('confidence')})")

    # Image 2: Breakfast JPEG
    bf_bytes = load_image_bytes(IMG_BREAKFAST, (180, 200, 90))
    
    res2 = client.post("/api/scan/ingredients", files={"file": ("breakfast.jpg", bf_bytes, "image/jpeg")})
    assert res2.status_code == 200, f"Breakfast scan failed: {res2.text}"
    data2 = res2.json()
    print(f"Image 2 (Breakfast JPG) Scan Result: Provider={data2.get('provider')}, Ingredients={len(data2.get('ingredients', []))}")
    for ing in data2.get("ingredients", []):
        print(f"  - {ing['name']}: {ing.get('estimated_quantity')} {ing.get('unit')} (conf: {ing.get('confidence')})")

    # Image 3: Converted PNG Format
    img_obj = Image.new("RGB", (300, 300), color=(220, 120, 60))
    png_io = io.BytesIO()
    img_obj.save(png_io, format="PNG")
    png_bytes = png_io.getvalue()
    
    res3 = client.post("/api/scan/ingredients", files={"file": ("ingredients.png", png_bytes, "image/png")})
    assert res3.status_code == 200, f"PNG scan failed: {res3.text}"
    print(f"Image 3 (PNG) Scan Result: Provider={res3.json().get('provider')}, Ingredients={len(res3.json().get('ingredients', []))}")

    # Image 4: Converted WEBP Format
    webp_io = io.BytesIO()
    img_obj.save(webp_io, format="WEBP")
    webp_bytes = webp_io.getvalue()
    
    res4 = client.post("/api/scan/ingredients", files={"file": ("ingredients.webp", webp_bytes, "image/webp")})
    assert res4.status_code == 200, f"WEBP scan failed: {res4.text}"
    print(f"Image 4 (WEBP) Scan Result: Provider={res4.json().get('provider')}, Ingredients={len(res4.json().get('ingredients', []))}")

    # Test Invalid File Format (text file)
    res_inv = client.post("/api/scan/ingredients", files={"file": ("test.txt", b"hello world", "text/plain")})
    assert res_inv.status_code == 400, f"Expected 400 for invalid file type, got {res_inv.status_code}"
    print("Invalid mime type test passed (HTTP 400 details):", res_inv.json()["detail"])

    # Test Oversized File (>10MB)
    huge_bytes = b"0" * (11 * 1024 * 1024)
    res_huge = client.post("/api/scan/ingredients", files={"file": ("huge.jpg", huge_bytes, "image/jpeg")})
    assert res_huge.status_code == 400, f"Expected 400 for oversized file, got {res_huge.status_code}"
    print("Oversized file test passed (HTTP 400 details):", res_huge.json()["detail"])

    return data1.get("ingredients", [])

def test_meal_scans():
    print("\n--- 3. Testing Prepared Meal Scan (/api/scan/meal) ---")
    meal_bytes = load_image_bytes(IMG_MEAL, (100, 150, 200))

    res = client.post("/api/scan/meal", files={"file": ("meal.jpg", meal_bytes, "image/jpeg")})
    assert res.status_code == 200, f"Meal scan failed: {res.text}"
    data = res.json()
    print("Meal Scan Result:", json.dumps(data, indent=2))
    assert "meal" in data or "meal_name" in data.get("meal", {}), "Meal data missing in response"

def test_recipe_matching(scanned_ingredients):
    print("\n--- 4. Testing Recipe Match Engine (/api/recipes/find) ---")
    
    # 4a. Find with scanned ingredients
    res1 = client.post("/api/recipes/find", json={"ingredients": scanned_ingredients, "filters": {}, "include_pantry": True})
    assert res1.status_code == 200
    rdata1 = res1.json()
    print(f"Recipes found with scanned ingredients & pantry: {rdata1['count']}")
    for r in rdata1["recipes"][:3]:
        print(f"  - {r['name']} ({r['match_percentage']}% match, {r['match_summary']}) - Health Score: {r['health_score']['score']}")

    # 4b. Find with High Protein filter
    res2 = client.post("/api/recipes/find", json={"ingredients": scanned_ingredients, "filters": {"high_protein": True}})
    assert res2.status_code == 200
    print(f"High Protein recipes count: {res2.json()['count']}")

    # 4c. Find with Under 20 min filter
    res3 = client.post("/api/recipes/find", json={"ingredients": scanned_ingredients, "filters": {"under_20": True}})
    assert res3.status_code == 200
    print(f"Under 20 min recipes count: {res3.json()['count']}")

    # 4d. Find with Vegetarian filter
    res4 = client.post("/api/recipes/find", json={"ingredients": scanned_ingredients, "filters": {"vegetarian": True}})
    assert res4.status_code == 200
    print(f"Vegetarian recipes count: {res4.json()['count']}")

def test_recipe_detail_and_improve():
    print("\n--- 5. Testing Recipe Detail & 'Improve My Meal' ---")
    # Get first recipe ID
    r_list = client.post("/api/recipes/find", json={"ingredients": []}).json()["recipes"]
    if not r_list:
        print("No recipes found in DB!")
        return
    
    rec_id = r_list[0]["id"]
    print(f"Testing Recipe ID: {rec_id} ({r_list[0]['name']})")

    # Detail at 2 servings
    r_det2 = client.get(f"/api/recipes/{rec_id}?servings=2")
    assert r_det2.status_code == 200
    d2 = r_det2.json()
    print(f"Recipe Detail (2 servings): {d2['name']}, Servings={d2['servings']}, Total Cost={d2['estimated_cost']}")

    # Scale to 4 servings
    r_det4 = client.get(f"/api/recipes/{rec_id}?servings=4")
    assert r_det4.status_code == 200
    d4 = r_det4.json()
    print(f"Recipe Detail (4 servings): Servings={d4['servings']}, Total Cost={d4['estimated_cost']}")
    assert d4['servings'] == 4

    # Improve Meal
    improve_req = {
        "servings": 2,
        "reduce_oil": True,
        "add_veggies": True,
        "boost_protein": True,
        "substitutions": {"paneer": "tofu"}
    }
    res_imp = client.post(f"/api/recipes/{rec_id}/improve", json=improve_req)
    assert res_imp.status_code == 200, f"Improve meal failed: {res_imp.text}"
    imp_data = res_imp.json()
    print("Improve My Meal Response:")
    print("  - Applied Changes:", imp_data["applied_changes"])
    print("  - Original Health Score:", imp_data["original_health_score"])
    print("  - Improved Health Score:", imp_data["improved_health_score"])
    print("  - Summary:", imp_data["changes_summary"])

def test_pantry_crud():
    print("\n--- 6. Testing Pantry Inventory CRUD (/api/pantry) ---")
    # GET
    r_get = client.get("/api/pantry")
    assert r_get.status_code == 200
    items_before = r_get.json()
    print(f"Initial pantry item count: {len(items_before)}")

    # POST (Add new item)
    new_item = {"ingredient": "Garlic", "quantity": 50, "unit": "g", "freshness": "Fresh"}
    r_add = client.post("/api/pantry", json=new_item)
    assert r_add.status_code == 200
    added = r_add.json()
    print(f"Added pantry item: ID={added['id']}, Ingredient={added['ingredient']}")

    # PUT (Update item)
    r_upd = client.put(f"/api/pantry/{added['id']}", json={"quantity": 100, "freshness": "Use Soon"})
    assert r_upd.status_code == 200
    print(f"Updated item: Quantity={r_upd.json()['quantity']}, Freshness={r_upd.json()['freshness']}")

    # DELETE
    r_del = client.delete(f"/api/pantry/{added['id']}")
    assert r_del.status_code == 200
    print(f"Deleted item ID {added['id']} status: {r_del.json()['status']}")

def test_nutrition_and_meals():
    print("\n--- 7. Testing Daily Nutrition & Meal Log (/api/nutrition/today & /api/meals) ---")
    # GET Today's summary
    r_nut = client.get("/api/nutrition/today")
    assert r_nut.status_code == 200
    summary = r_nut.json()
    print("Today's Nutrition Summary:", summary["consumed"])

    # POST Log a meal
    log_payload = {
        "meal_name": "Paneer Tikka Roll",
        "meal_type": "Lunch",
        "calories": 450,
        "protein": 22.0,
        "carbs": 48.0,
        "fat": 18.0,
        "fiber": 6.0
    }
    r_log = client.post("/api/meals", json=log_payload)
    assert r_log.status_code == 200
    logged = r_log.json()
    print(f"Logged meal: ID={logged['id']}, Meal={logged['meal_name']}, Calories={logged['calories']}")

    # Check updated today's summary
    r_nut2 = client.get("/api/nutrition/today")
    print("Updated Today's Consumed Calories:", r_nut2.json()["consumed"]["calories"])

def test_shopping_list():
    print("\n--- 8. Testing Shopping List CRUD (/api/shopping-list) ---")
    r_shop = client.get("/api/shopping-list")
    assert r_shop.status_code == 200
    print(f"Current shopping list count: {len(r_shop.json())}")

    # Add item
    r_add = client.post("/api/shopping-list", json={"ingredient": "Olive Oil", "quantity": 1, "unit": "bottle"})
    assert r_add.status_code == 200
    item = r_add.json()
    print(f"Added to shopping list: {item['ingredient']}")

    # Toggle purchased
    r_prog = client.put(f"/api/shopping-list/{item['id']}", json={"purchased": True})
    assert r_prog.status_code == 200
    print(f"Marked purchased: {r_prog.json()['purchased']}")

    # Delete item
    r_del = client.delete(f"/api/shopping-list/{item['id']}")
    assert r_del.status_code == 200
    print(f"Deleted shopping item ID {item['id']}")

def test_assistant():
    print("\n--- 9. Testing Ask NutriScan AI Assistant (/api/assistant/ask) ---")
    ask_payload = {
        "question": "How can I increase protein in my paneer curry?",
        "context": {"recipe_name": "Paneer Butter Masala", "current_ingredients": ["paneer", "tomato", "butter"]}
    }
    r_ast = client.post("/api/assistant/ask", json=ask_payload)
    assert r_ast.status_code == 200
    ast_resp = r_ast.json()
    print("Assistant Response:", ast_resp["answer"][:150] + "...")

if __name__ == "__main__":
    print("==========================================")
    print("  NUTRISCAN ALL-FEATURE TEST SUITE")
    print("==========================================")
    test_health()
    scanned_ings = test_ingredient_scans()
    test_meal_scans()
    test_recipe_matching(scanned_ings)
    test_recipe_detail_and_improve()
    test_pantry_crud()
    test_nutrition_and_meals()
    test_shopping_list()
    test_assistant()
    print("\n==========================================")
    print("  ALL 9 TEST SUITES PASSED SUCCESSFULLY! [OK]")
    print("==========================================")
