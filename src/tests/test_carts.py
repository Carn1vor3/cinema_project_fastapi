import decimal
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.main import app
from src.database import AsyncSessionLocal, engine, Base
from src.models.users import User, UserGroup, UserGroupEnum
from src.models.movies import Movies, Certifications
from src.models.carts import Carts, CartItems


@pytest_asyncio.fixture
async def test_db_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def sample_user(test_db_session: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        is_active=True,
        group=UserGroup(name="USER"),
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, sample_user: User):
    response = await async_client.post(
        "/auth/login", json={"email": sample_user.email, "password": "password123"}
    )
    assert response.status_code == 200, response.text
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


@pytest.mark.asyncio
async def test_add_movie_to_cart(
    async_client: AsyncClient, sample_movie: Movies, auth_headers
):
    response = await async_client.post(
        f"/cart/add/{sample_movie.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Movie added to cart."


@pytest.mark.asyncio
async def test_view_cart(
    async_client: AsyncClient,
    sample_movie: Movies,
    auth_headers,
    test_db_session: AsyncSession,
    sample_user: User,
):
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    response = await async_client.get("/cart/view", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == sample_movie.name
    assert data[0]["price"] == sample_movie.price


@pytest.mark.asyncio
async def test_remove_movie_from_cart(
    async_client: AsyncClient,
    sample_movie: Movies,
    auth_headers,
    test_db_session: AsyncSession,
    sample_user: User,
):
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    response = await async_client.delete(
        f"/cart/remove/{sample_movie.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Movie removed from cart."


@pytest.mark.asyncio
async def test_clear_cart(
    async_client: AsyncClient,
    sample_movie: Movies,
    auth_headers,
    test_db_session: AsyncSession,
    sample_user: User,
):
    cart = Carts(user_id=sample_user.id)
    test_db_session.add(cart)
    await test_db_session.flush()
    item = CartItems(cart_id=cart.id, movie_id=sample_movie.id)
    test_db_session.add(item)
    await test_db_session.commit()

    response = await async_client.delete("/cart/clear", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Cart cleared."
