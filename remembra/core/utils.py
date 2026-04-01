"""General utility helpers used across modules."""

from datetime import UTC, datetime


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""

    return datetime.now(UTC).isoformat()
