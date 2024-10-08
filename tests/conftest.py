import os
from dotenv import load_dotenv
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from main import app
from database.base import Base
from database.connection import get_session

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL_TEST")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL_TEST environment variable is not set")


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    yield create_async_engine(DATABASE_URL, poolclass=NullPool, echo=True)


@pytest.fixture(scope="session", autouse=True)
async def initialize_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_session(engine):
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client(test_session):
    app.dependency_overrides[get_session] = lambda: test_session
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://localhost"
    ) as client:
        yield client
    app.dependency_overrides.clear()
