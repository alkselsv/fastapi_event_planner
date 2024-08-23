import os
from dotenv import load_dotenv
from asyncio import current_task
from typing import AsyncGenerator
from database.base import Base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncEngine,
    AsyncSession,
)

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL_PROD")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async_session = async_scoped_session(session_maker, scopefunc=current_task)

    async with async_session() as session:
        yield session
