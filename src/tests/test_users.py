import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


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

    # спочатку реєструємо користувача
    await async_client.post("/users/register", json=payload)

    response = await async_client.post(
        "/users/resend-activation", params={"email": email}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "New activation link sent"
