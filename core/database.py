from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config.settings import Settings

_engine = None
_session_factory = None


class Base(DeclarativeBase):
    pass


def init_engine(settings: Settings):
    global _engine, _session_factory
    connect_args = {}
    if "sqlite" in settings.database_url:
        connect_args = {"check_same_thread": False}
    _engine = create_async_engine(
        settings.database_url,
        connect_args=connect_args,
        echo=False,
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine


def get_engine():
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session_factory():
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_engine() first.")
    return _session_factory


async def get_db_session() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def create_tables():
    from core.models import Base as ModelsBase  # noqa: F401
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)
