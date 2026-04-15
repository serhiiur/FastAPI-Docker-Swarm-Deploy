import logging
from collections.abc import AsyncIterator, Coroutine
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, TypedDict, cast

from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastcrud import crud_router
from pydantic import BaseModel, EmailStr, Field, PositiveInt, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import func
from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)
from sqlmodel import Field as SQLField
from sqlmodel import SQLModel


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

  _env_file = Path("/run/configs/api.env")
  _secrets_dir = Path("/run/secrets")
  model_config = SettingsConfigDict(
    env_file=_env_file if _env_file.exists() else None,
    secrets_dir=_secrets_dir if _secrets_dir.is_dir() else None,
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

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_logger(request: Request) -> logging.Logger:
  """Return logger object initialized in the lifespan."""
  return cast("logging.Logger", request.state.logger)


async def get_db_session() -> AsyncIterator[AsyncSession]:
  """Yield a database session to be used as a dependency."""
  async with async_session() as session:
    yield session


class Timestamp(BaseModel):
  """Schema to specify timestamp field containing the current timestamp."""

  timestamp: str = Field(
    description="Current timestamp in ISO format",
    default_factory=lambda: datetime.now(UTC).isoformat(),
    examples=["2026-04-13T11:48:12.258255+00:00"],
  )


class InternalServerError(Timestamp):
  """Response schema to specify an internal server error for the client."""

  detail: str = "service is temporarily unavailable"
  path: str


class Base(SQLModel):
  """Base declarative SQL model."""

  id: int | None = SQLField(default=None, primary_key=True)
  created_at: datetime = SQLField(default_factory=func.now)
  updated_at: datetime = SQLField(
    default_factory=func.now,
    sa_column_kwargs={"onupdate": func.now},
  )


class CreateUser(SQLModel):
  """Request schema to create a user."""

  name: str = SQLField(
    description="Name of the user",
  )
  email: EmailStr = SQLField(
    description="Email of the user",
    unique=True,
    index=True,
  )
  age: PositiveInt = SQLField(
    description="Age of the user",
  )
  is_employed: bool = SQLField(
    default=True,
    description="Whether the user is employed or not",
  )


class UpdateUser(SQLModel):
  """Request schema to update a user."""

  name: str | None = SQLField(
    default=None,
    description="Optional new name of the user",
  )
  email: EmailStr | None = SQLField(
    default=None,
    description="Optional new email of the user",
  )
  age: PositiveInt | None = SQLField(
    default=None,
    description="Optional new age of the user",
  )
  is_employed: bool | None = SQLField(
    default=None,
    description="Optional new employment status",
  )


class User(Base, CreateUser, table=True):
  """Database model to represent a user in the database."""


async def internal_server_error_handler(
  request: Request,
  _exc: Exception,
) -> JSONResponse:
  """Error handler for all unhandled errors."""
  return JSONResponse(
    content=InternalServerError(path=request.url.path).model_dump(),
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
  )


# error handlers mapping to be registered in the main FastAPI app
error_handlers: dict[
  int | type[Exception],
  Callable[[Request, Any], Coroutine[Any, Any, Response]],
] = {
  Exception: internal_server_error_handler,
}


class ApiVersion(Timestamp):
  """Response schema to provide info about API version."""

  version: str = Field(
    default=settings.fastapi_kwargs["version"],
    description="Version of the API",
    examples=[settings.fastapi_kwargs["version"]],
  )


class ApiHealth(Timestamp):
  """Response schema to provide info about API health status."""

  status: str = Field(
    default="ok",
    description="Health status of the API",
    examples=["ok"],
  )


class AppState(TypedDict):
  """Data structure to represent state of the main application."""

  logger: "logging.Logger"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
  """Run database migrations and define application state objects."""
  logger = getattr(app.state, "logger", logging.getLogger(settings.logger_name))
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield AppState(logger=logger)


app = FastAPI(
  **settings.fastapi_kwargs,
  exception_handlers=error_handlers,
  lifespan=lifespan,
)

internal_router = APIRouter(prefix="/api", tags=["internal"])


@internal_router.get("/version")
async def version() -> ApiVersion:
  """Return information about API version."""
  return ApiVersion.model_construct()


@internal_router.get("/health")
async def health() -> ApiHealth:
  """Return information about API health status."""
  return ApiHealth.model_construct()


app.include_router(internal_router)

# CRUD router for managing users
user_router = crud_router(
  session=get_db_session,
  model=User,
  create_schema=CreateUser,
  update_schema=UpdateUser,
  path="/api/users",
  tags=["users"],
)
app.include_router(user_router)
