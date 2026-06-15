from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import get_settings


def create_database_engine():
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for database access")
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
