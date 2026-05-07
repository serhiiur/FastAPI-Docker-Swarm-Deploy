from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.db import engine
from app.core.errors import error_handlers
from app.core.routes import router as core_router
from app.core.settings import settings
from app.users.routes import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Run database migrations and define application state objects."""
    # startup actions
    yield
    # shutdown actions
    await engine.dispose()


app = FastAPI(
    **settings.fastapi.model_dump(),
    exception_handlers=error_handlers,
    lifespan=lifespan,
)
app.include_router(core_router)
app.include_router(user_router)
