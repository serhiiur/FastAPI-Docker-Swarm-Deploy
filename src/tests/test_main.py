from typing import TYPE_CHECKING

import pytest
from fastapi import status

from app.core.schemas import ApiHealth, ApiVersion

if TYPE_CHECKING:
  from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_health(client: "AsyncClient") -> None:
  resp = await client.get("/api/health")
  assert resp.status_code == status.HTTP_200_OK
  assert resp.json() == ApiHealth.model_construct().model_dump()


async def test_version(client: "AsyncClient") -> None:
  resp = await client.get("/api/version")
  assert resp.status_code == status.HTTP_200_OK
  assert resp.json() == ApiVersion.model_construct().model_dump()
