from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, cast

from fastapi import Request

from .db import async_session

if TYPE_CHECKING:
  from logging import Logger

  from sqlalchemy.ext.asyncio import AsyncSession


async def get_logger(request: Request) -> "Logger":
  """Return logger object initialized in the lifespan."""
  return cast("Logger", request.state.logger)


async def get_db_session() -> AsyncIterator["AsyncSession"]:
  """Yield a database session to be used as a dependency."""
  async with async_session() as session:
    yield session
