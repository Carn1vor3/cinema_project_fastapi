import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy import select

from src.models.users import User
from src.database import get_db
from src.main import app


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_db_session():
    async for session in get_db():
        yield session


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    payload = {"email": "testuser@example.com", "password": "StrongP@ssw0rd!"}
    response = await async_client.post("/users/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == payload["email"]
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_resend_activation(async_client: AsyncClient):
    email = "resend@example.com"
    payload = {"email": email, "password": "StrongP@ssw0rd!"}

    await async_client.post("/users/register", json=payload)

    response = await async_client.post(
        "/users/resend-activation", params={"email": email}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "New activation link sent"
