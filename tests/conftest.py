import os
from dotenv import load_dotenv
import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from typing import AsyncGenerator
from sqlalchemy.pool import NullPool

from main import app
from database.base import Base
from database.connection import get_session


load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL_TEST")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="module")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    await init_db()
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://localhost"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        try:
            yield session
        finally:
            session.close()
