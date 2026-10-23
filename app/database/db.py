from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.models import Base
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Global engine and sessionmaker (initialized once)
_engine = None
_SessionLocal = None

def init_db(database_url: str = None):
    """
    Initialize the database engine and create tables.
    :param database_url: SQLAlchemy database URL (overrides config if provided)
    """
    global _engine, _SessionLocal
    url = database_url or DATABASE_URL
    logger.info(f"Initializing database with URL: {url}")
    _engine = create_engine(url, echo=False, future=True)
    # Create all tables
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, class_=Session, future=True)
    logger.info("Database initialized successfully.")

def get_session(database_url: str = None) -> Session:
    """
    Get a new database session.
    :param database_url: SQLAlchemy database URL (if provided, will reinitialize engine if different)
    :return: SQLAlchemy Session object
    """
    global _engine, _SessionLocal
    url = database_url or DATABASE_URL
    # If engine not initialized or URL changed, reinitialize
    if _engine is None or str(_engine.url) != url:
        init_db(url)
    return _SessionLocal()