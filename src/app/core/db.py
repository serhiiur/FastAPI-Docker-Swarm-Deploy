from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import settings

engine = create_async_engine(settings.db.url, echo=settings.fastapi.debug)
async_session = async_sessionmaker(engine, expire_on_commit=False)
