"""FastAPI entrypoint for EchoMind."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from echomind.api.routes import router
from echomind.core.logging import configure_logging
from echomind.core.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown lifecycle hooks."""

    settings = get_settings()
    configure_logging(level=settings.log_level)
    yield


def create_app() -> FastAPI:
    """Application factory for API service."""

    app = FastAPI(
        title="EchoMind API",
        description="Non-clinical in-silico memory cue research backend.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
