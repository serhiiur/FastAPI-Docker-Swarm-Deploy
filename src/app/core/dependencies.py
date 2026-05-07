from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Annotated, TypeAlias

from fastapi import Depends

from .db import async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncIterator["AsyncSession"]:
    """Yield a database session to be used as a dependency."""
    async with async_session() as session:
        yield session


DbSession: TypeAlias = Annotated["AsyncSession", Depends(get_db_session)]
