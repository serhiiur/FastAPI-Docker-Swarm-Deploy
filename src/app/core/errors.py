from collections.abc import Coroutine
from typing import Any, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from .schemas import InternalServerError


async def internal_server_error_handler(
  request: Request,
  _exc: Exception,
) -> JSONResponse:
  """Error handler for all unhandled errors."""
  return JSONResponse(
    content=InternalServerError(path=request.url.path).model_dump(),
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
  )


# error handlers mapping to be registered in the main FastAPI app
error_handlers: dict[
  int | type[Exception],
  Callable[[Request, Any], Coroutine[Any, Any, Response]],
] = {
  Exception: internal_server_error_handler,
}
