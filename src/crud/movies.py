from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.movies import Movies, Stars, Genres, Directors
from schemas.movies import MovieListSchema, MovieCreateSchema, MovieUpdateSchema, GenresCreateSchema, \
    GenresUpdateSchema, StarsUpdateSchema, StarsCreateSchema, StarsListSchema, GenresListSchema, DirectorsListSchema

from typing import List, Optional
from schemas.movies import MovieListSchema


### Movie Model CRUD ###


async def get_movies(
        limit: int,
        offset: int,
        db: AsyncSession,
        year: Optional[int] = None,
        imdb: Optional[float] = None,
        meta_score: Optional[float] = None,
        search: Optional[str] = None,
        year_sort: bool = False,
        imdb_sort: bool = False,
        meta_score_sort: bool = False,
) -> List[MovieListSchema]:
    query = (
        select(Movies)
        .options(
            selectinload(Movies.stars),
            selectinload(Movies.genres),
            selectinload(Movies.directors)
        )
        .offset(offset)
        .limit(limit)
    )
    if year is not None:
        query = query.filter(Movies.year == year)
    if imdb is not None:
        query = query.filter(Movies.imdb == imdb)
    if meta_score is not None:
        query = query.filter(Movies.meta_score == meta_score)

    order_by_list = []
    if year_sort:
        order_by_list.append(Movies.year.desc())
    if imdb_sort:
        order_by_list.append(Movies.imdb.desc())
    if meta_score_sort:
        order_by_list.append(Movies.meta_score.desc())

    if order_by_list:
        query = query.order_by(*order_by_list)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Movies.name.ilike(search_pattern),
                Movies.description.ilike(search_pattern),
                Movies.stars.any(Stars.name.ilike(search_pattern)),
                Movies.directors.any(Directors.name.ilike(search_pattern))
            )
        )


    result = await db.execute(query)
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
                stars=[StarsListSchema.from_orm(s) for s in m.stars],
                genres=[GenresListSchema.from_orm(g) for g in m.genres],
                directors=[DirectorsListSchema.from_orm(d) for d in m.directors]
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
        stars=[StarsListSchema.from_orm(s) for s in movie.stars],
        genres=[GenresListSchema.from_orm(g) for g in movie.genres],
        directors=[DirectorsListSchema.from_orm(d) for d in movie.directors]
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

async def update_movie(movie_id: int, new_movie: MovieUpdateSchema, db: AsyncSession):
    result = await db.execute(
        select(Movies)
        .options(
            selectinload(Movies.stars),
            selectinload(Movies.genres),
            selectinload(Movies.directors),
        )
        .where(Movies.id == movie_id)
    )
    movie_to_update = result.scalar_one_or_none()

    if not movie_to_update:
        raise HTTPException(status_code=404, detail="Movie not found")

    if new_movie.uuid:
        movie_to_update.uuid = new_movie.uuid
    if new_movie.name:
        movie_to_update.name = new_movie.name
    if new_movie.year:
        movie_to_update.year = new_movie.year
    if new_movie.time:
        movie_to_update.time = new_movie.time
    if new_movie.imdb:
        movie_to_update.imdb = new_movie.imdb
    if new_movie.votes:
        movie_to_update.votes = new_movie.votes
    if new_movie.meta_score:
        movie_to_update.meta_score = new_movie.meta_score
    if new_movie.gross:
        movie_to_update.gross = new_movie.gross
    if new_movie.description:
        movie_to_update.description = new_movie.description
    if new_movie.price:
        movie_to_update.price = new_movie.price
    if new_movie.certification_id:
        movie_to_update.certification_id = new_movie.certification_id

    if new_movie.stars_ids:
        result = await db.execute(select(Stars).where(Stars.id.in_(new_movie.stars_ids)))
        movie_to_update.stars = result.scalars().all()


    if new_movie.genres_ids:
        result = await db.execute(select(Genres).where(Genres.id.in_(new_movie.genres_ids)))
        movie_to_update.genres = result.scalars().all()


    if new_movie.directors_ids:
        result = await db.execute(select(Directors).where(Directors.id.in_(new_movie.directors_ids)))
        movie_to_update.directors = result.scalars().all()




    db.add(movie_to_update)
    await db.commit()
    await db.refresh(movie_to_update)

    return movie_to_update


### Stars Model CRUD ###


async def get_stars(db: AsyncSession):
    result = await db.execute(select(Stars))
    stars_list = result.scalars().all()
    if not stars_list:
        raise HTTPException(status_code=404, detail="Stars not found")
    return stars_list

async def get_star_by_id(star_id: int, db: AsyncSession):
    result = await db.execute(select(Stars).where(Stars.id == star_id))
    star = result.scalar_one_or_none()
    if not star:
        raise HTTPException(status_code=404, detail="Star not found")
    return star

async def create_star(new_star: StarsCreateSchema, db: AsyncSession):
    star = Stars(
        name=new_star.name,
    )
    db.add(star)
    await db.commit()
    await db.refresh(star)
    return star

async def delete_star(star_id: int, db: AsyncSession):
    result = await db.execute(select(Stars).where(Stars.id == star_id))
    star = result.scalar_one_or_none()
    if not star:
        raise HTTPException(status_code=404, detail="Star not found")
    await db.delete(star)
    await db.commit()
    return {"detail": f"Star with id {star.id} deleted successfully"}

async def update_star(star_id: int, new_star_data: StarsUpdateSchema, db: AsyncSession):
    result = await db.execute(select(Stars).where(Stars.id == star_id))
    star = result.scalar_one_or_none()
    if not star:
        raise HTTPException(status_code=404, detail="Star not found")

    star.name = new_star_data.name

    db.add(star)
    await db.commit()
    await db.refresh(star)
    return star


### Genres Model CRUD ###

async def get_genres(db: AsyncSession):
    result = await db.execute(select(Genres))
    genres = result.scalars().all()
    if not genres:
        raise HTTPException(status_code=404, detail="Stars not found")
    return genres

async def get_genre_by_id(genre_id: int, db: AsyncSession):
    result = await db.execute(select(Genres).where(Genres.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre

async def create_genre(new_genre: GenresCreateSchema, db: AsyncSession):
    genre = Genres(
        name=new_genre.name,
    )
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre

async def delete_genre(genre_id: int, db: AsyncSession):
    result = await db.execute(select(Genres).where(Genres.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    await db.delete(genre)
    await db.commit()
    return {"detail": f"Genre with id {genre.id} deleted successfully"}

async def update_genre(genre_id: int, new_genre_data: GenresUpdateSchema, db: AsyncSession):
    result = await db.execute(select(Genres).where(Genres.id == genre_id))
    genre = result.scalar_one_or_none()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    genre.name = new_genre_data.name
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


