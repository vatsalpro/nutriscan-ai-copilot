import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "NutriScan API"
    VERSION: str = "3.1.0"

    # Provider 1 (Primary): OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL",
        "openrouter/free"
    ).strip()
    OPENROUTER_VISION_MODEL: str = os.getenv(
        "OPENROUTER_VISION_MODEL",
        os.getenv("OPENROUTER_MODEL", "openrouter/free")
    ).strip()
    OPENROUTER_SITE_URL: str = os.getenv(
        "OPENROUTER_SITE_URL",
        "https://nutriscan-ai.vercel.app"
    ).strip()

    # Provider 2 (Secondary Fallback): Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "qwen/qwen3.8-27b"
    ).strip()
    GROQ_VISION_MODEL: str = os.getenv(
        "GROQ_VISION_MODEL",
        "qwen/qwen3.8-27b"
    ).strip()

    # Provider 3 (Final Fallback): Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash"
    ).strip()
    GEMINI_VISION_MODEL: str = os.getenv(
        "GEMINI_VISION_MODEL",
        os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    ).strip()

    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "20"))
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    default_db = "/tmp/nutriscan.db" if os.getenv("VERCEL") else "./nutriscan.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")


settings = Settings()
