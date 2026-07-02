from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ingestion.config import get_settings


@lru_cache
def create_database_engine() -> Engine:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for ingestion database access")
    return create_engine(settings.database_url, pool_pre_ping=True)


def create_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=create_database_engine(), autoflush=False, autocommit=False)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = create_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
