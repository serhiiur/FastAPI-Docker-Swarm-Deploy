from typing import TYPE_CHECKING

from fastapi import status

from app.core.schemas import ApiHealth, ApiVersion

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_health(client: "AsyncClient") -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == status.HTTP_200_OK
    api_health_schema = ApiHealth()
    resp_json = resp.json()
    assert resp_json.get("status") == api_health_schema.status
    assert "timestamp" in resp_json


async def test_version(client: "AsyncClient") -> None:
    resp = await client.get("/api/version")
    assert resp.status_code == status.HTTP_200_OK
    api_version_schema = ApiVersion()
    resp_json = resp.json()
    assert resp_json.get("version") == api_version_schema.version
    assert "timestamp" in resp_json
