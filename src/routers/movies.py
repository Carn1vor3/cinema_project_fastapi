from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.movies import (
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
from src.database import get_db
from src.models.base import user_favorites
from src.models.movies import Movies, Stars, Directors, MovieRating
from src.models.users import User
from src.schemas.movies import (
    MovieListSchema,
    MovieCreateSchema,
    MovieUpdateSchema,
    GenresListSchema,
    GenresCreateSchema,
    GenresUpdateSchema,
    StarsListSchema,
    StarsCreateSchema,
    StarsUpdateSchema,
    GenresWithCountSchema,
    GenresDetailSchema,
    MovieLikeCreate,
    MovieCommentOut,
    MovieCommentCreate,
    MovieRatingCreate,
)
from src.services.movies import toggle_like_movie, add_comment_movie
from src.services.users import get_current_user

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


@router.post("/like-toggle", tags=["Likes, comments and favourites"])
async def like_toggle(
    data: MovieLikeCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await toggle_like_movie(user, data.movie_id, db)


@router.post(
    "/comment", response_model=MovieCommentOut, tags=["Likes, comments and favourites"]
)
async def comment_movie(
    data: MovieCommentCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await add_comment_movie(user, data.movie_id, data.content, db)


@router.post("/favorites/{movie_id}", tags=["Likes, comments and favourites"])
async def add_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.favorite_movies))
        .where(User.id == current_user.id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie in user.favorite_movies:
        return {"detail": "Movie already in favorites"}

    user.favorite_movies.append(movie)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"detail": f"Movie '{movie.name}' added to favorites"}


@router.delete("/favorites/{movie_id}", tags=["Likes, comments and favourites"])
async def remove_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.favorite_movies))
        .where(User.id == current_user.id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    if movie not in user.favorite_movies:
        raise HTTPException(status_code=400, detail="Movie not in favorites")

    user.favorite_movies.remove(movie)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"detail": f"Movie '{movie.name}' removed from favorites"}


@router.get("/favorites/", tags=["Likes, comments and favourites"])
async def get_favorites(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year: int | None = None,
    imdb: float | None = None,
    meta_score: float | None = None,
    search: str | None = None,
    year_sort: bool = False,
    imdb_sort: bool = False,
    meta_score_sort: bool = False,
):
    query = (
        select(Movies)
        .join(user_favorites, Movies.id == user_favorites.c.movie_id)
        .where(user_favorites.c.user_id == current_user.id)
        .options(
            selectinload(Movies.stars),
            selectinload(Movies.genres),
            selectinload(Movies.directors),
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
                Movies.directors.any(Directors.name.ilike(search_pattern)),
            )
        )

    result = await db.execute(query)
    movies = result.scalars().all()
    return movies


@router.post("/rate/{movie_id}", tags=["Likes, comments and favourites"])
async def rate_movie(
    movie_id: int,
    rating_data: MovieRatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.favorite_movies))
        .where(User.id == current_user.id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalars().first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = await db.execute(
        select(MovieRating)
        .where(MovieRating.movie_id == movie_id)
        .where(MovieRating.user_id == current_user.id)
    )
    existing_rating = result.scalars().first()

    if existing_rating:
        existing_rating.rating = rating_data.rating
    else:
        new_rating = MovieRating(
            user_id=current_user.id, movie_id=movie_id, rating=rating_data.rating
        )
        db.add(new_rating)

    await db.commit()
    return {"detail": f"Movie '{movie.name}' rated {rating_data.rating}/10"}
