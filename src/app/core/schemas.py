from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .settings import settings


class Timestamp(BaseModel):
  """Schema to specify timestamp field containing the current timestamp."""

  timestamp: str = Field(
    description="Current timestamp in ISO format",
    default_factory=lambda: datetime.now(UTC).isoformat(),
    examples=["2026-04-13T11:48:12.258255+00:00"],
  )


class InternalServerError(Timestamp):
  """Response schema to specify an internal server error for the client."""

  detail: str = "service is temporarily unavailable"
  path: str


class ApiVersion(Timestamp):
  """Response schema to provide info about API version."""

  version: str = Field(
    default=settings.fastapi_kwargs["version"],
    description="Version of the API",
    examples=[settings.fastapi_kwargs["version"]],
  )


class ApiHealth(Timestamp):
  """Response schema to provide info about API health status."""

  status: str = Field(
    default="ok",
    description="Health status of the API",
    examples=["ok"],
  )
