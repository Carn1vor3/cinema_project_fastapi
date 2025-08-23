from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.movies import Movies, MovieLike, MovieComment
from src.models.users import User


async def toggle_like_movie(user: User, movie_id: int, db: AsyncSession):
    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise ValueError("Movie not found")

    result = await db.execute(
        select(MovieLike).where(
            MovieLike.user_id == user.id, MovieLike.movie_id == movie_id
        )
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        await db.delete(existing_like)
        await db.commit()
        return {"message": "Movie unliked"}
    else:
        like = MovieLike(user_id=user.id, movie_id=movie_id)
        db.add(like)
        await db.commit()
        return {"message": "Movie liked"}


async def add_comment_movie(user: User, movie_id: int, content: str, db: AsyncSession):
    result = await db.execute(select(Movies).where(Movies.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise ValueError("Movie not found")

    comment = MovieComment(user_id=user.id, movie_id=movie_id, content=content)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment
