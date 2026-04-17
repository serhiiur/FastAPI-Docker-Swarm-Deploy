from fastapi import APIRouter

from .schemas import ApiHealth, ApiVersion

router = APIRouter(prefix="/api", tags=["internal"])


@router.get("/version")
async def version() -> ApiVersion:
  """Return information about API version."""
  return ApiVersion.model_construct()


@router.get("/health")
async def health() -> ApiHealth:
  """Return information about API health status."""
  return ApiHealth.model_construct()
