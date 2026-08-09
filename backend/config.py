import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "NutriScan API"
    VERSION: str = "3.0.0"

    # Provider 1: Groq / Llama 3.3 70B
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    ).strip()

    # Provider 2: OpenRouter / Google Gemma 4 free variant
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "").strip()
    OPENROUTER_MODEL: str = os.getenv(
        "OPENROUTER_MODEL",
        "google/gemma-4-26b-a4b-it:free"
    ).strip()
    OPENROUTER_SITE_URL: str = os.getenv(
        "OPENROUTER_SITE_URL",
        "https://nutriscan-ai-copilot.onrender.com"
    ).strip()

    # Provider 3: OpenRouter free-model router
    OPENROUTER_FREE_MODEL: str = os.getenv(
        "OPENROUTER_FREE_MODEL",
        "openrouter/free"
    ).strip()

    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "45"))
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./nutriscan.db"
    )


settings = Settings()
