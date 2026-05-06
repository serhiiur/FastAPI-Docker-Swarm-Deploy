from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.dependencies import get_db_session, get_logger, get_settings
from app.core.settings import TestSettings
from app.main import app
from tests.dependencies import (
    override_get_db_session,
    override_get_logger,
    override_get_settings,
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Async backend for pytest."""
    return "asyncio"


settings = TestSettings()
db_engine = create_async_engine(settings.db.url)

# Override main application dependencies for testing
app.dependency_overrides[get_settings] = override_get_settings(settings)
app.dependency_overrides[get_logger] = override_get_logger(settings.logger.name)
app.dependency_overrides[get_db_session] = override_get_db_session(db_engine)


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[AsyncClient]:
    """Yield async HTTP client, preserving application lifespan events."""
    async with LifespanManager(app) as manager:
        transport = ASGITransport(manager.app)
        base_url = "http://test"
        async with AsyncClient(base_url=base_url, transport=transport) as client:
            yield client
