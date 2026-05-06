import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.settings import TestSettings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


def override_get_settings(
    settings: TestSettings,
) -> Callable[[], Awaitable[TestSettings]]:
    """Override `get_settings` dependency during testing.

    :param settings: settings to be used during testing
    :return: settings to be used during testing
    """

    async def get_settings() -> TestSettings:
        return settings

    return get_settings


def override_get_db_session(
    engine: "AsyncEngine",
) -> Callable[[], AsyncIterator["AsyncSession"]]:
    """Override `get_db_session` dependency during testing.

    :param engine: SQLAlchemy's database engine to be used during testing
    :return: async generator that yields a database session
    """

    async def get_db_session() -> AsyncIterator["AsyncSession"]:
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            yield session

    return get_db_session


def override_get_logger(name: str) -> Callable[[], Awaitable[logging.Logger]]:
    """Override `get_logger` dependency during testing.

    :param name: name of the logger to use during testing
    :return: logger to be used during testing
    """

    async def get_logger() -> logging.Logger:
        return logging.getLogger(name)

    return get_logger
