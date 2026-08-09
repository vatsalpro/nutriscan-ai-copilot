from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Hackathon Chef")
    email = Column(String, unique=True, index=True, default="chef@nutriscan.ai")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class IngredientDB(Base):
    __tablename__ = "ingredients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, default="General")
    unit = Column(String, default="g")
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    price_per_unit = Column(Float, default=0.0)
    icon = Column(String, default="🥗")

class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    ingredient = Column(String, nullable=False)
    quantity = Column(Float, default=100.0)
    unit = Column(String, default="g")
    freshness = Column(String, default="Fresh") # "Fresh", "Use Soon", "Expiring Soon"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RecipeDB(Base):
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    prep_time = Column(Integer, default=10)
    cook_time = Column(Integer, default=15)
    servings = Column(Integer, default=2)
    difficulty = Column(String, default="Medium")
    image_url = Column(String, nullable=True)
    tags_json = Column(Text, default="[]")
    estimated_cost = Column(Float, default=100.0)
    steps_json = Column(Text, default="[]")
    substitutions_json = Column(Text, default="[]")
    improvements_json = Column(Text, default="[]")

class RecipeIngredientDB(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False, index=True)
    ingredient = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="g")


class MealLogDB(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    recipe_id = Column(String, nullable=True)
    meal_name = Column(String, nullable=False)
    meal_type = Column(String, default="Lunch") # "Breakfast", "Lunch", "Snack", "Dinner"
    servings = Column(Float, default=1.0)
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ShoppingListItemDB(Base):
    __tablename__ = "shopping_list"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)
    ingredient = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="g")
    purchased = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
