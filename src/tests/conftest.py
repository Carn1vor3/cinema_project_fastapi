import asyncio
import decimal
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx._transports.asgi import ASGITransport

from src.models.movies import Certifications, Movies
from src.core.security import hash_password
from src.models.users import User, UserGroup
from src.main import app
from src.database import Base, get_db, engine, AsyncSessionLocal

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def sample_movie(test_db_session: AsyncSession) -> Movies:
    certification = Certifications(name="Certification")
    test_db_session.add(certification)
    await test_db_session.commit()
    await test_db_session.refresh(certification)

    movie = Movies(
        uuid=uuid.uuid4(),
        name="Test Movie",
        year=2023,
        time=120,
        imdb=8.5,
        votes=1000,
        meta_score=75.0,
        gross=5000000.0,
        description="Test description",
        price=decimal.Decimal("10.00"),
        certification_id=certification.id,
    )
    test_db_session.add(movie)
    await test_db_session.commit()
    await test_db_session.refresh(movie)
    return movie


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, sample_user: User):
    response = await async_client.post(
        "/auth/login", json={"email": sample_user.email, "password": "password123"}
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def test_db():
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db):
    async with test_db() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def sample_user(test_db_session: AsyncSession) -> User:
    plain_password = "password123"

    result = await test_db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalars().first()
    if user:
        return user
    result = await test_db_session.execute(
        select(UserGroup).where(UserGroup.name == "USER")
    )
    group = result.scalars().first()
    if not group:
        group = UserGroup(name="USER")
        test_db_session.add(group)
        await test_db_session.commit()
        await test_db_session.refresh(group)

    user = User(
        email="test@example.com",
        hashed_password=hash_password(plain_password),
        is_active=True,
        group_id=group.id,
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    user._plain_password = plain_password
    return user


