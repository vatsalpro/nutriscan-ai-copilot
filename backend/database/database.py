from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
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
