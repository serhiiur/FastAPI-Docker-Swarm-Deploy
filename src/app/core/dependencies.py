import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Annotated, TypeAlias

from fastapi import Depends

from .db import async_session
from .settings import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from .settings import Settings as AppSettings


async def get_settings() -> "AppSettings":
    """Return settings object to be used as a dependency."""
    return settings


Settings: TypeAlias = Annotated["AppSettings", Depends(get_settings)]


async def get_logger(settings: Settings) -> logging.Logger:
    """Return logger object initialized in the lifespan."""
    return logging.getLogger(settings.logger.name)


Logger: TypeAlias = Annotated[logging.Logger, Depends(get_logger)]


async def get_db_session() -> AsyncIterator["AsyncSession"]:
    """Yield a database session to be used as a dependency."""
    async with async_session() as session:
        yield session


DbSession: TypeAlias = Annotated["AsyncSession", Depends(get_db_session)]
