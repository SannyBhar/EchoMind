"""Celery worker entrypoint."""

from echomind.core.celery_app import create_celery_app

celery_app = create_celery_app()


@celery_app.task(name="echomind.health.ping")
def ping() -> str:
    """Simple task used for worker smoke validation."""

    return "pong"
