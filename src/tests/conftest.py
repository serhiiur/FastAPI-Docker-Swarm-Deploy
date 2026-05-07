from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Async backend for pytest."""
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncIterator[AsyncClient]:
    """Yield async HTTP client, preserving application lifespan events."""
    async with LifespanManager(app) as manager:
        transport = ASGITransport(manager.app)
        base_url = "http://test"
        async with AsyncClient(base_url=base_url, transport=transport) as client:
            yield client
