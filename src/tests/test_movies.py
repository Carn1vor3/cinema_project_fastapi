import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from src.main import app
from src.schemas.movies import MovieCreateSchema


@pytest.mark.asyncio
async def test_create_movie(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "uuid": str(uuid4()),
        "name": "Test Movie",
        "year": 2025,
        "time": 120,
        "imdb": 8.5,
        "votes": 1000,
        "meta_score": 85.0,
        "gross": 1000000.0,
        "description": "A test movie",
        "price": 9.99,
        "certification_id": 1,
        "stars_ids": [],
        "genres_ids": [],
        "directors_ids": [],
    }

    response = await client.post("/movies", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_list_movies(client: AsyncClient):
    response = await client.get("/movies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_movie_by_id(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "uuid": str(uuid4()),
        "name": "GetByID Movie",
        "year": 2025,
        "time": 100,
        "imdb": 7.0,
        "votes": 500,
        "meta_score": 70.0,
        "gross": 500000.0,
        "description": "Movie for get by id",
        "price": 5.99,
        "certification_id": 1,
        "stars_ids": [],
        "genres_ids": [],
        "directors_ids": [],
    }
    create_resp = await client.post("/movies", json=payload)
    movie_id = create_resp.json()["id"]

    response = await client.get(f"/movies/{movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == movie_id
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_delete_movie(client: AsyncClient, db_session: AsyncSession):
    payload = {
        "uuid": str(uuid4()),
        "name": "Delete Movie",
        "year": 2025,
        "time": 90,
        "imdb": 6.5,
        "votes": 300,
        "meta_score": 60.0,
        "gross": 200000.0,
        "description": "Movie to delete",
        "price": 4.99,
        "certification_id": 1,
        "stars_ids": [],
        "genres_ids": [],
        "directors_ids": [],
    }
    create_resp = await client.post("/movies", json=payload)
    movie_id = create_resp.json()["id"]

    response = await client.delete(f"/movies/{movie_id}")
    assert response.status_code == 200
    data = response.json()
    assert "detail" in data
    assert str(movie_id) in data["detail"]
