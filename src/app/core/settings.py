from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FastApiKwargs(TypedDict):
  """Data structure to specify kwargs for FastAPI application."""

  title: str
  description: str
  debug: bool
  version: str
  docs_url: str
  redoc_url: str
  openapi_url: str


class Settings(BaseSettings):
  """Application settings."""

  _root_path: Path = Path(__file__).parents[3]
  _env_file = _root_path / "configs" / "api.env"
  _secrets_dir = _root_path / "secrets"

  model_config = SettingsConfigDict(
    env_file=_env_file,
    secrets_dir=_secrets_dir,
    extra="ignore",
  )

  # FastAPI settings
  title: str = "FastAPI Template"
  description: str = "Starter FastAPI application."
  debug: bool = False
  version: str = "0.0.1"
  docs_url: str = "/api/schema/docs"
  redoc_url: str = "/api/schema/redoc"
  openapi_url: str = "/api/schema/openapi.json"

  # Database settings
  db_password: str = ""

  # Other settings
  logger_name: str = "uvicorn.error"

  @computed_field
  @property
  def database_url(self) -> str:
    """Dynamically set database URL."""
    if not self.db_password:
      return "sqlite+aiosqlite:///fastapi.db"
    return f"postgresql+asyncpg://postgres:{self.db_password}@db:5432/postgres"

  @property
  def fastapi_kwargs(self) -> FastApiKwargs:
    """Kwargs for FastAPI application."""
    return FastApiKwargs(
      title=self.title,
      description=self.description,
      debug=self.debug,
      version=self.version,
      docs_url=self.docs_url,
      redoc_url=self.redoc_url,
      openapi_url=self.openapi_url,
    )


@lru_cache
def get_settings() -> Settings:
  """Return cached project settings."""
  return Settings()


settings = get_settings()
