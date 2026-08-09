import json
import os
from sqlalchemy.orm import Session
from database.database import engine, SessionLocal, Base
from database.models import User, IngredientDB, RecipeDB, RecipeIngredientDB, PantryItem, ShoppingListItemDB, MealLogDB

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Default User
        user = db.query(User).filter_index_property if hasattr(db.query(User), 'filter_index_property') else db.query(User).first()
        if not user:
            user = User(id=1, name="Hackathon Chef", email="chef@nutriscan.ai")
            db.add(user)
            db.commit()

        # 2. Seed Ingredients
        ing_file = os.path.join(os.path.dirname(__file__), "..", "data", "ingredients.json")
        if os.path.exists(ing_file):
            with open(ing_file, "r", encoding="utf-8") as f:
                ingredients_data = json.load(f)
                for item in ingredients_data:
                    existing = db.query(IngredientDB).filter(IngredientDB.id == item["id"]).first()
                    if not existing:
                        ing = IngredientDB(
                            id=item["id"],
                            name=item["name"],
                            category=item.get("category", "General"),
                            unit=item.get("unit", "g"),
                            calories=item.get("calories", 0.0),
                            protein=item.get("protein", 0.0),
                            carbs=item.get("carbs", 0.0),
                            fat=item.get("fat", 0.0),
                            fiber=item.get("fiber", 0.0),
                            price_per_unit=item.get("price_per_unit", 0.0),
                            icon=item.get("icon", "🥗")
                        )
                        db.add(ing)
            db.commit()

        # 3. Seed Recipes
        rec_file = os.path.join(os.path.dirname(__file__), "..", "data", "recipes.json")
        if os.path.exists(rec_file):
            with open(rec_file, "r", encoding="utf-8") as f:
                recipes_data = json.load(f)
                for rec in recipes_data:
                    existing = db.query(RecipeDB).filter(RecipeDB.id == rec["id"]).first()
                    if not existing:
                        recipe = RecipeDB(
                            id=rec["id"],
                            name=rec["name"],
                            description=rec.get("description", ""),
                            prep_time=rec.get("prep_time", 10),
                            cook_time=rec.get("cook_time", 15),
                            servings=rec.get("servings", 2),
                            difficulty=rec.get("difficulty", "Medium"),
                            image_url=rec.get("image_url", ""),
                            tags_json=json.dumps(rec.get("tags", [])),
                            estimated_cost=rec.get("estimated_cost", 100.0),
                            steps_json=json.dumps(rec.get("steps", [])),
                            substitutions_json=json.dumps(rec.get("substitutions", [])),
                            improvements_json=json.dumps(rec.get("improvements", []))
                        )
                        db.add(recipe)
                        
                        # Add Recipe Ingredients
                        for ing_item in rec.get("ingredients", []):
                            rec_ing = RecipeIngredientDB(
                                recipe_id=rec["id"],
                                ingredient=ing_item["ingredient"],
                                quantity=ing_item["quantity"],
                                unit=ing_item.get("unit", "g")
                            )
                            db.add(rec_ing)
            db.commit()

        # 4. Initial Pantry Items for smooth demo
        pantry_count = db.query(PantryItem).count()
        if pantry_count == 0:
            demo_pantry = [
                {"ingredient": "paneer", "quantity": 200, "unit": "g", "freshness": "Fresh"},
                {"ingredient": "potato", "quantity": 250, "unit": "g", "freshness": "Fresh"},
                {"ingredient": "tomato", "quantity": 150, "unit": "g", "freshness": "Use Soon"},
                {"ingredient": "onion", "quantity": 100, "unit": "g", "freshness": "Fresh"},
                {"ingredient": "capsicum", "quantity": 80, "unit": "g", "freshness": "Use Soon"},
                {"ingredient": "rice", "quantity": 500, "unit": "g", "freshness": "Fresh"},
                {"ingredient": "spinach", "quantity": 150, "unit": "g", "freshness": "Expiring Soon"},
            ]
            for p in demo_pantry:
                db.add(PantryItem(user_id=1, ingredient=p["ingredient"], quantity=p["quantity"], unit=p["unit"], freshness=p["freshness"]))
            db.commit()

        # 5. Initial Shopping List
        shop_count = db.query(ShoppingListItemDB).count()
        if shop_count == 0:
            db.add(ShoppingListItemDB(user_id=1, ingredient="cumin", quantity=1, unit="tsp", purchased=False))
            db.add(ShoppingListItemDB(user_id=1, ingredient="coriander", quantity=1, unit="tbsp", purchased=False))
            db.commit()

        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
