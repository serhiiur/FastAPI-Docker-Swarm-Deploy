import os
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import AppEnvironment


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

    name: str = ""
    user: str = ""
    password: str = ""
    url: str = "sqlite+aiosqlite:///local.db"

    @model_validator(mode="after")
    def set_url(self) -> Self:
        """Set the database URL after validating the provided database parameters."""
        if all([self.name, self.user, self.password]):
            self.url = (
                f"postgresql+asyncpg://{self.user}:{self.password}@db:5432/{self.name}"
            )
        return self


class LoggingSettings(BaseAbstractSettings):
    """Settings for logging configuration."""

    model_config = SettingsConfigDict(env_prefix="log_")

    name: str = "uvicorn.error"


class DefaultSettings(BaseAbstractSettings):
    """Default application settings."""

    fastapi: FastApiSettings = FastApiSettings()
    db: DatabaseSettings = DatabaseSettings()
    logger: LoggingSettings = LoggingSettings()


class TestSettings(DefaultSettings):
    """Settings for testing environment of the application."""

    fastapi: FastApiSettings = FastApiSettings(debug=True)
    logger: LoggingSettings = LoggingSettings(name="test")


class DevelopmentSettings(DefaultSettings):
    """Settings for development environment of the application."""

    fastapi: FastApiSettings = FastApiSettings(debug=True)


class ProductionSettings(DefaultSettings):
    """Settings for production environment of the application."""

    fastapi: FastApiSettings = FastApiSettings(debug=False)


@lru_cache
def get_settings() -> DefaultSettings:
    """Return cached project settings."""
    environment = os.getenv("APP_ENVIRONMENT", AppEnvironment.PRODUCTION)
    match environment:
        case AppEnvironment.PRODUCTION:
            return ProductionSettings()
        case AppEnvironment.TEST:
            return TestSettings()
        case AppEnvironment.DEVELOPMENT:
            return DevelopmentSettings()
        case _:
            return DefaultSettings()


settings = get_settings()
