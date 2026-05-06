from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAbstractSettings(BaseSettings):
    """Base class for settings of the application."""

    _root_path: Path = Path(__file__).parents[3]
    _env_file = _root_path / "configs" / "api.env"
    _secrets_dir = _root_path / "secrets"

    model_config = SettingsConfigDict(
        env_file=_env_file,
        secrets_dir=_secrets_dir,
        extra="ignore",
    )


class FastApiSettings(BaseAbstractSettings):
    """Settings for FastAPI application."""

    model_config = SettingsConfigDict(env_prefix="fastapi_")

    title: str = "FastAPI Template"
    description: str = "Starter FastAPI application."
    debug: bool = False
    version: str = "0.0.1"
    docs_url: str = "/api/schema/docs"
    redoc_url: str = "/api/schema/redoc"
    openapi_url: str = "/api/schema/openapi.json"


class DatabaseSettings(BaseAbstractSettings):
    """Settings for database connection."""

    model_config = SettingsConfigDict(env_prefix="db_")

    password: str = ""
    url: str = (
        "sqlite+aiosqlite:///local.db"
        if not password
        else f"postgresql+asyncpg://postgres:{password}@db:5432/postgres"
    )


class LoggingSettings(BaseAbstractSettings):
    """Settings for logging configuration."""

    model_config = SettingsConfigDict(env_prefix="log_")

    name: str = "uvicorn.error"


class Settings(BaseAbstractSettings):
    """Application settings."""

    fastapi: FastApiSettings = FastApiSettings()
    db: DatabaseSettings = DatabaseSettings()
    logger: LoggingSettings = LoggingSettings()


class TestSettings(BaseAbstractSettings):
    """Settings to be used during testing."""

    fastapi: FastApiSettings = FastApiSettings(debug=True)
    logger: LoggingSettings = LoggingSettings(name="test")
    db: DatabaseSettings = DatabaseSettings()


@lru_cache
def get_settings() -> Settings:
    """Return cached project settings."""
    return Settings()


settings = get_settings()
