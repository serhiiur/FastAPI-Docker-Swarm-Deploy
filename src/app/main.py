import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI

from app.core.errors import error_handlers
from app.core.routes import router as core_router
from app.core.settings import settings
from app.users.routes import router as user_router


class AppState(TypedDict):
  """Data structure to represent state of the main application."""

  logger: "logging.Logger"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
  """Run database migrations and define application state objects."""
  logger = getattr(app.state, "logger", logging.getLogger(settings.logger_name))
  yield AppState(logger=logger)


app = FastAPI(
  **settings.fastapi_kwargs,
  exception_handlers=error_handlers,
  lifespan=lifespan,
)
app.include_router(core_router)
app.include_router(user_router)
