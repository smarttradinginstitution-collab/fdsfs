import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient

from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for an async client to make requests to the app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
