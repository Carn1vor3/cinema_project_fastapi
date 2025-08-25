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
from src.models.users import User, UserGroup
from src.models.carts import Carts, CartItems
from src.main import app
from src.database import Base, get_db
from src.core.security import hash_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ------------------ Async DB Fixtures ------------------

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(test_db_session):
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


# ------------------ Sample Data Fixtures ------------------

@pytest_asyncio.fixture
async def sample_user(test_db_session: AsyncSession):
    # Створюємо групу користувача
    result = await test_db_session.execute(select(UserGroup).where(UserGroup.name == "USER"))
    group = result.scalars().first()
    if not group:
        group = UserGroup(name="USER")
        test_db_session.add(group)
        await test_db_session.commit()
        await test_db_session.refresh(group)

    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        is_active=True,
        group_id=group.id
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    user._plain_password = "password123"
    return user


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, sample_user: User):
    response = await async_client.post(
        "/auth/login", json={"email": sample_user.email, "password": sample_user._plain_password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


# ------------------ Orders Tests ------------------

@pytest.mark.asyncio
async def test_create_order(async_client, sample_user, sample_movie, auth_headers, test_db_session):
    # Додаємо фільм у корзину
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    response = await async_client.post("/orders/", json={"movies_ids": [sample_movie.id]}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Order created successfully."
    assert len(data["ordered_movies"]) == 1
    assert data["ordered_movies"][0]["id"] == sample_movie.id


@pytest.mark.asyncio
async def test_get_my_orders(async_client, sample_user, sample_movie, auth_headers, test_db_session):
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    # Створюємо замовлення
    await async_client.post("/orders/", json={"movies_ids": [sample_movie.id]}, headers=auth_headers)

    response = await async_client.get("/orders/me", headers=auth_headers)
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    assert orders[0]["items"][0]["movie_id"] == sample_movie.id


@pytest.mark.asyncio
async def test_cancel_order(async_client, sample_user, sample_movie, auth_headers, test_db_session):
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    resp = await async_client.post("/orders/", json={"movies_ids": [sample_movie.id]}, headers=auth_headers)
    order_id = resp.json()["order"]["id"]

    cancel_resp = await async_client.post(f"/orders/{order_id}/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["status"] == "success"
    assert data["order_id"] == order_id
    assert data["new_status"] == "canceled"
