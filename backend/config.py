import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "NutriScan API"
    VERSION: str = "3.0.0"

    # Provider 1: Groq / Meta Llama 4 Scout
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "meta-llama/llama-4-scout-17b-16e-instruct"
    ).strip()

    # Provider 2: OpenRouter / Google Gemma 4 free variant
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL",
        "google/gemma-4-26b-a4b-it:free"
    ).strip()
    OPENROUTER_SITE_URL: str = os.getenv(
        "OPENROUTER_SITE_URL",
        "https://nutriscan-ai.vercel.app"
    ).strip()

    # Provider 3: OpenRouter free-model router
    OPENROUTER_FREE_MODEL: str = os.getenv(
        "OPENROUTER_FREE_MODEL",
        "openrouter/free"
    ).strip()

    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "45"))
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    default_db = "/tmp/nutriscan.db" if os.getenv("VERCEL") else "./nutriscan.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{default_db}")


settings = Settings()
