"""Shared FastAPI dependencies for API routes."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from echomind.db.session import get_db_session


def db_session_dependency() -> Generator[Session, None, None]:
    """Expose database session dependency wrapper for route modules."""

    yield from get_db_session()
