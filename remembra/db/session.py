"""Database engine and session management utilities."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from remembra.core.settings import get_settings


def build_engine(database_url: str | None = None) -> Engine:
    """Build a SQLAlchemy engine from explicit URL or app settings."""

    resolved_url = database_url or get_settings().database_url
    return create_engine(resolved_url, future=True, pool_pre_ping=True)


def build_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Build a session factory for a given engine."""

    bound_engine = engine or build_engine()
    return sessionmaker(bind=bound_engine, autoflush=False, autocommit=False, class_=Session)


engine = build_engine()
SessionLocal = build_session_factory(engine)


@contextmanager
def session_scope(
    session_factory: sessionmaker[Session] | None = None,
) -> Generator[Session, None, None]:
    """Provide a transactional session scope."""

    factory = session_factory or SessionLocal
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Generator[Session, None, None]:
    """Yield a DB session for request-scoped use."""

    with session_scope() as session:
        yield session
