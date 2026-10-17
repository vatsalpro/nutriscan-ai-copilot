import os
import tempfile
from pathlib import Path
from typing import List
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

    DEFAULT_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "https://nutriscan-ai.vercel.app",
        "https://nutriscan-ai-copilot.vercel.app",
    ]

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        raw = os.getenv("ALLOWED_ORIGINS", "")
        env_origins = [
            o.strip().rstrip("/")
            for o in raw.split(",")
            if o.strip() and o.strip() != "*"
        ]
        merged: List[str] = []
        for origin in env_origins + self.DEFAULT_ORIGINS:
            if origin and origin not in merged:
                merged.append(origin)
        return merged

    _raw_db_url: str = os.getenv("DATABASE_URL", "").strip()
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

    if os.getenv("VERCEL"):
        # Vercel serverless functions have an ephemeral, read-only project filesystem;
        # use the OS temp directory (/tmp/nutriscan.db on Linux) unless an external DATABASE_URL is configured.
        if not _raw_db_url or "./nutriscan.db" in _raw_db_url or _raw_db_url.endswith("/nutriscan.db"):
            DATABASE_URL: str = f"sqlite:///{(Path(tempfile.gettempdir()) / 'nutriscan.db').as_posix()}"
        else:
            DATABASE_URL: str = _raw_db_url
    else:
        DATABASE_URL: str = _raw_db_url or f"sqlite:///{(BACKEND_DIR / 'nutriscan.db').as_posix()}"


settings = Settings()
