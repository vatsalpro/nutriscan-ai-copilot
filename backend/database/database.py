from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

from config import settings

logger = logging.getLogger(__name__)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    try:
        db = SessionLocal()
        try:
            recipe_count = db.query(models.RecipeDB).count()
        finally:
            db.close()
        if recipe_count == 0:
            from database.seed import seed_database
            seed_database()
    except Exception as exc:
        logger.warning("Auto-seed check failed: %s", exc)


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
