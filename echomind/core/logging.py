"""Logging helpers for service entrypoints."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure basic structured logging for bootstrap services."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
