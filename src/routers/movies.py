from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.movies import get_movies, get_movie_by_id, delete_movie, create_movie
from database import get_db
from schemas.movies import MovieListSchema, MovieCreateSchema

router = APIRouter()

@router.get("/movies", response_model=list[MovieListSchema])
async def list_movies(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await get_movies(limit=limit, offset=offset, db=db)


@router.get("/movies/{movie_id}", response_model=MovieListSchema)
async def detail_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await get_movie_by_id(movie_id=movie_id, db=db)


@router.delete("/movies/{movie_id}")
async def remove_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_movie(movie_id=movie_id, db=db)


@router.post("/movies", response_model=MovieListSchema)
async def add_movie(movie_data: MovieCreateSchema, db: AsyncSession = Depends(get_db)):
    return await create_movie(movie_data=movie_data, db=db)
