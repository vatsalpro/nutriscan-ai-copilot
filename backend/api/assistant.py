from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from config import settings
from database.database import get_db
from database.models import RecipeDB
from sqlalchemy.orm import Session
from services.ai_router import ai_router

router = APIRouter(prefix="/api/assistant", tags=["assistant"])
logger = logging.getLogger(__name__)


class AssistantRequest(BaseModel):
    query: Optional[str] = None
    question: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    current_recipe: Optional[Any] = None
    user_ingredients: Optional[Any] = None


@router.post("/ask")
async def ask_assistant(req: AssistantRequest, db: Session = Depends(get_db)):
    query = (req.query or req.question or "").strip()
    recipe_input = req.current_recipe or (req.context or {}).get("recipe_name")
    ingredients_input = req.user_ingredients or (req.context or {}).get("current_ingredients") or []

    recipe_context = "No recipe selected."
    if isinstance(recipe_input, str) and recipe_input.strip():
        rec = db.query(RecipeDB).filter(RecipeDB.id == recipe_input.strip()).first()
        recipe_context = (
            f"Current Recipe: {rec.name} ({rec.description})"
            if rec
            else f"Current Recipe: {recipe_input.strip()}"
        )
    elif isinstance(recipe_input, dict):
        recipe_context = f"Current Recipe: {recipe_input.get('name') or recipe_input.get('id') or ''}"

    ing_names = []
    if isinstance(ingredients_input, list):
        for item in ingredients_input:
            if isinstance(item, str):
                ing_names.append(item)
            elif isinstance(item, dict):
                ing_names.append(item.get("name") or item.get("ingredient") or "")
    ing_context = (
        f"Available user ingredients: {', '.join(i for i in ing_names if i)}"
        if any(ing_names)
        else "No ingredients provided."
    )

    medical_keywords = [
        "cure", "disease", "treatment", "medicine", "diabetes",
        "hypertension", "medical diagnosis", "allergy reaction", "doctor",
    ]
    if any(k in query.lower() for k in medical_keywords):
        text = (
            "NutriScan provides general culinary and dietary information and is "
            "not a substitute for professional medical or health advice. For "
            "specific medical questions, consult a qualified physician or dietitian."
        )
        return {"response": text, "answer": text, "type": "disclaimer"}

    if ai_router.active:
        try:
            system = """You are NutriScan AI Kitchen Assistant.
Give concise, practical cooking guidance based on the user's context.
Do not provide medical diagnosis, treatment, or prescriptions.
If quantities are discussed, call them estimates unless they come from the recipe.
Prefer 2-4 useful bullets or a short paragraph."""
            prompt = f"""Context:
{recipe_context}
{ing_context}

User question:
{query}"""
            result = ai_router.text(prompt, system=system, max_tokens=450)
            response_text = result["text"]
            if response_text:
                return {
                    "response": response_text,
                    "answer": response_text,
                    "type": "ai",
                    "provider": result["provider"],
                    "model": result["model"],
                    "fallback": result["is_fallback"],
                }
        except Exception as exc:
            logger.exception("All AI assistant providers failed: %s", exc)

    # Explicit fallback for temporary inference outages.
    q = query.lower()
    if "tomato" in q or "no tomatoes" in q:
        reply = "Try tomato paste, tamarind, curd, or lemon juice depending on the recipe."
    elif "protein" in q:
        reply = "Try adding paneer, tofu, eggs, chickpeas, lentils, or Greek yogurt."
    elif "replace paneer" in q or "substitute paneer" in q:
        reply = "Firm tofu is the closest 1:1 substitute; chickpeas or eggs can also work depending on the dish."
    elif "cheaper" in q or "budget" in q:
        reply = "Use seasonal vegetables, lentils, chickpeas, or eggs to lower the cost while keeping the meal filling."
    elif "quick" in q or "15 minutes" in q:
        reply = "For a quick meal, use pre-cut vegetables, eggs, leftover rice, or a simple stir-fry."
    else:
        reply = "The AI kitchen assistant is temporarily unavailable. Please try again in a moment."

    return {"response": reply, "answer": reply, "type": "fallback"}
