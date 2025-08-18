from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.movies import (
    get_movies,
    get_movie_by_id,
    delete_movie,
    create_movie,
    update_movie,
    get_genres,
    get_genre_by_id,
    create_genre,
    delete_genre,
    update_genre,
    get_stars,
    get_star_by_id,
    create_star,
    delete_star,
    update_star,
)
from database import get_db
from schemas.movies import (
    MovieListSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    GenresListSchema,
    GenresCreateSchema,
    GenresUpdateSchema,
    StarsListSchema,
    StarsCreateSchema,
    StarsUpdateSchema, GenresWithCountSchema, GenresDetailSchema,
)

router = APIRouter()


@router.get("/movies", response_model=list[MovieListSchema], tags=["Movies"])
async def list_movies(
    year: Optional[int] = None,
    imdb: Optional[float] = None,
    meta_score: Optional[float] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    year_sort: bool = False,
    imdb_sort: bool = False,
    meta_score_sort: bool = False,
    search: Optional[str] = None,
):
    return await get_movies(
        limit=limit,
        offset=offset,
        year=year,
        imdb=imdb,
        meta_score=meta_score,
        db=db,
        year_sort=year_sort,
        imdb_sort=imdb_sort,
        meta_score_sort=meta_score_sort,
        search=search,
    )


@router.get("/movies/{movie_id}", response_model=MovieListSchema, tags=["Movies"])
async def detail_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await get_movie_by_id(movie_id=movie_id, db=db)


@router.delete("/movies/{movie_id}", tags=["Movies"])
async def remove_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_movie(movie_id=movie_id, db=db)


@router.post("/movies", response_model=MovieListSchema, tags=["Movies"])
async def add_movie(movie_data: MovieCreateSchema, db: AsyncSession = Depends(get_db)):
    return await create_movie(movie_data=movie_data, db=db)


@router.patch("/movies/{movie_id}", response_model=MovieListSchema, tags=["Movies"])
async def put_movie(
    movie_id: int, new_movie: MovieUpdateSchema, db: AsyncSession = Depends(get_db)
):
    return await update_movie(movie_id=movie_id, new_movie=new_movie, db=db)


@router.get("/genres", response_model=List[GenresWithCountSchema], tags=["Genres"])
async def list_genres(db: AsyncSession = Depends(get_db)):
    return await get_genres(db=db)


@router.get("/genres/{genre_id}", response_model=GenresDetailSchema, tags=["Genres"])
async def detail_genres(genre_id: int, db: AsyncSession = Depends(get_db)):
    return await get_genre_by_id(genre_id=genre_id, db=db)


@router.post("/genres", response_model=GenresListSchema, tags=["Genres"])
async def post_genres(
    new_genre: GenresCreateSchema, db: AsyncSession = Depends(get_db)
):
    return await create_genre(new_genre=new_genre, db=db)


@router.delete("/genres/{genre_id}", tags=["Genres"])
async def remove_genre(genre_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_genre(genre_id=genre_id, db=db)


@router.put("/genres/{genre_id}", response_model=GenresListSchema, tags=["Genres"])
async def put_genre(
    genre_id: int,
    new_genre_data: GenresUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    return await update_genre(genre_id=genre_id, new_genre_data=new_genre_data, db=db)


@router.get("/stars", response_model=List[StarsListSchema], tags=["Stars"])
async def list_stars(db: AsyncSession = Depends(get_db)):
    return await get_stars(db=db)


@router.get("/stars/{star_id}", response_model=StarsListSchema, tags=["Stars"])
async def detail_stars(star_id: int, db: AsyncSession = Depends(get_db)):
    return await get_star_by_id(star_id=star_id, db=db)


@router.post("/stars", response_model=StarsListSchema, tags=["Stars"])
async def post_stars(new_star: StarsCreateSchema, db: AsyncSession = Depends(get_db)):
    return await create_star(new_star=new_star, db=db)


@router.delete("/stars/{star_id}", tags=["Stars"])
async def remove_star(star_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_star(star_id=star_id, db=db)


@router.put("/stars/{star_id}", response_model=StarsListSchema, tags=["Stars"])
async def put_stars(
    star_id: int, new_star_data: StarsUpdateSchema, db: AsyncSession = Depends(get_db)
):
    return await update_star(star_id=star_id, new_star_data=new_star_data, db=db)
