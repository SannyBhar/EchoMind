"""Celery app factory for worker bootstrap."""

from celery import Celery

from echomind.core.settings import get_settings


def create_celery_app() -> Celery:
    """Create Celery app configured via shared settings."""

    settings = get_settings()
    app = Celery(
        "echomind",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
    return app
