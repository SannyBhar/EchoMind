"""Application settings for the EchoMind scaffold."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized environment-backed settings."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ECHOMIND_", extra="ignore")

    env: str = Field(default="dev")
    log_level: str = Field(default="INFO")

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    dashboard_port: int = Field(default=8501)

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/echomind"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")

    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings to avoid repeated env parsing."""

    return Settings()
