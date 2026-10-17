import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend directory is on sys.path for both local and Vercel serverless execution
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import settings
from api import scan, recipes, pantry, nutrition, shopping, assistant

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.ai_router import ai_router
    logger.info(
        "NutriScan API ready. AI providers active: %s; providers=%s",
        ai_router.active,
        list(ai_router.configured_models.keys()),
    )
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="NutriScan API - AI Kitchen Copilot & Nutrition Engine",
    lifespan=lifespan,
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


# CORS setup — uses explicit origin allowlist (never wildcard '*' with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Include API Routers
app.include_router(scan.router)
app.include_router(recipes.router)
app.include_router(pantry.router)
app.include_router(nutrition.router)
app.include_router(shopping.router)
app.include_router(assistant.router)


@app.get("/")
@app.get("/api")
@app.get("/api/")
def root():
    from services.ai_router import ai_router
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION,
        "ai_active": ai_router.active,
        "configured_models": ai_router.configured_models,
        "provider_order": [name for name, _ in ai_router.providers],
        "failover_enabled": True,
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
