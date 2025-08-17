from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.movies import Movies, Stars, Genres, Directors
from schemas.movies import MovieListSchema, MovieCreateSchema


from typing import List
from schemas.movies import MovieListSchema

async def get_movies(limit: int, offset: int, db: AsyncSession) -> List[MovieListSchema]:
    result = await db.execute(
        select(Movies)
        .options(
            selectinload(Movies.stars),
            selectinload(Movies.genres),
            selectinload(Movies.directors)
        )
        .offset(offset)
        .limit(limit)
    )
    movies = result.scalars().all()

    movies_list = []
    for m in movies:
        movies_list.append(
            MovieListSchema(
                id=m.id,
                uuid=m.uuid,
                name=m.name,
                year=m.year,
                time=m.time,
                imdb=m.imdb,
                votes=m.votes,
                meta_score=m.meta_score,
                gross=m.gross,
                description=m.description,
                price=m.price,
                certification_id=m.certification_id,
                stars_ids=[s.id for s in m.stars],
                genres_ids=[g.id for g in m.genres],
                directors_ids=[d.id for d in m.directors]
            )
        )

    return movies_list



async def get_movie_by_id(movie_id: int, db: AsyncSession):
    result = await db.execute(
        select(Movies)
        .options(
            selectinload(Movies.stars),
            selectinload(Movies.genres),
            selectinload(Movies.directors)
        )
        .where(Movies.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return MovieListSchema(
        id=movie.id,
        uuid=movie.uuid,
        name=movie.name,
        year=movie.year,
        time=movie.time,
        imdb=movie.imdb,
        votes=movie.votes,
        meta_score=movie.meta_score,
        gross=movie.gross,
        description=movie.description,
        price=movie.price,
        certification_id=movie.certification_id,
        stars_ids=[s.id for s in movie.stars],
        genres_ids=[g.id for g in movie.genres],
        directors_ids=[d.id for d in movie.directors]
    )




async def delete_movie(movie_id: int, db: AsyncSession):
    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    await db.delete(movie)
    await db.commit()

    return {"detail": f"Movie with id {movie_id} deleted successfully"}


async def create_movie(movie_data: MovieCreateSchema, db: AsyncSession):
    new_movie = Movies(
        uuid=movie_data.uuid,
        name=movie_data.name,
        year=movie_data.year,
        time=movie_data.time,
        imdb=movie_data.imdb,
        votes=movie_data.votes,
        meta_score=movie_data.meta_score,
        gross=movie_data.gross,
        description=movie_data.description,
        price=movie_data.price,
        certification_id=movie_data.certification_id
    )

    # Підвантажуємо Many-to-Many об’єкти перед комітом
    stars_list = []
    if movie_data.stars_ids:
        result = await db.execute(select(Stars).where(Stars.id.in_(movie_data.stars_ids)))
        stars_list = result.scalars().all()
        new_movie.stars = stars_list

    genres_list = []
    if movie_data.genres_ids:
        result = await db.execute(select(Genres).where(Genres.id.in_(movie_data.genres_ids)))
        genres_list = result.scalars().all()
        new_movie.genres = genres_list

    directors_list = []
    if movie_data.directors_ids:
        result = await db.execute(select(Directors).where(Directors.id.in_(movie_data.directors_ids)))
        directors_list = result.scalars().all()
        new_movie.directors = directors_list

    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)

    return {
        "id": new_movie.id,
        "uuid": new_movie.uuid,
        "name": new_movie.name,
        "year": new_movie.year,
        "time": new_movie.time,
        "imdb": new_movie.imdb,
        "votes": new_movie.votes,
        "meta_score": new_movie.meta_score,
        "gross": new_movie.gross,
        "description": new_movie.description,
        "price": new_movie.price,
        "certification_id": new_movie.certification_id,
        "stars_ids": [s.id for s in stars_list],
        "genres_ids": [g.id for g in genres_list],
        "directors_ids": [d.id for d in directors_list]
    }
