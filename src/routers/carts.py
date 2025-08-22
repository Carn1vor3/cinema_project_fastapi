from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, UTC

from database import get_db
from models.carts import Carts, CartItems
from models.movies import Movies
from models.users import User, UserGroupEnum
from services.users import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/add/{movie_id}")
async def add_movie_to_cart(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await db.scalar(select(Carts).where(Carts.user_id == current_user.id))
    if not cart:
        cart = Carts(user_id=current_user.id)
        db.add(cart)
        await db.flush()

    existing_item = await db.scalar(
        select(CartItems).where(
            CartItems.cart_id == cart.id, CartItems.movie_id == movie_id
        )
    )
    if existing_item:
        raise HTTPException(status_code=400, detail="Movie already in cart.")

    item = CartItems(cart_id=cart.id, movie_id=movie_id, added_at=datetime.now(UTC))
    db.add(item)
    await db.commit()
    return {"message": "Movie added to cart."}


@router.delete("/remove/{movie_id}")
async def remove_movie_from_cart(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await db.scalar(select(Carts).where(Carts.user_id == current_user.id))
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    item = await db.scalar(
        select(CartItems).where(
            CartItems.cart_id == cart.id, CartItems.movie_id == movie_id
        )
    )
    if not item:
        raise HTTPException(status_code=404, detail="Movie not in cart.")

    await db.delete(item)
    await db.commit()
    return {"message": "Movie removed from cart."}


@router.get("/view")
async def view_cart(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    cart = await db.scalar(
        select(Carts)
        .where(Carts.user_id == current_user.id)
        .options(
            selectinload(Carts.items)
            .selectinload(CartItems.movie)
            .selectinload(Movies.genres)
        )
    )
    if not cart or not cart.items:
        return []

    result = []
    for item in cart.items:
        movie = item.movie
        result.append(
            {
                "title": movie.name,
                "price": movie.price,
                "year": movie.year,
                "genres": [g.name for g in movie.genres],
                "added_at": item.added_at,
            }
        )
    return result


@router.delete("/clear")
async def clear_cart(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    cart = await db.scalar(select(Carts).where(Carts.user_id == current_user.id))
    if not cart:
        return {"message": "Cart is already empty."}

    await db.execute(delete(CartItems).where(CartItems.cart_id == cart.id))
    await db.commit()
    return {"message": "Cart cleared."}


@router.get("/view/{user_id}")
async def view_user_cart_for_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.group.name not in [UserGroupEnum.ADMIN, UserGroupEnum.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not authorized.")

    cart = await db.scalar(
        select(Carts)
        .where(Carts.user_id == user_id)
        .options(
            selectinload(Carts.items)
            .selectinload(CartItems.movie)
            .selectinload(Movies.genres)
        )
    )
    if not cart or not cart.items:
        return []

    result = []
    for item in cart.items:
        movie = item.movie
        result.append(
            {
                "title": movie.name,
                "price": movie.price,
                "year": movie.year,
                "genres": [g.name for g in movie.genres],
                "added_at": item.added_at,
            }
        )
    return result


@router.delete("/admin/delete-movie/{movie_id}")
async def delete_movie_admin(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.group.name not in [UserGroupEnum.ADMIN, UserGroupEnum.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not authorized.")

    result = await db.execute(select(CartItems).where(CartItems.movie_id == movie_id))
    items_list = result.scalars().all()
    if items_list:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete movie {movie_id}. Exists in {len(items_list)} users' carts.",
        )

    movie = await db.scalar(select(Movies).where(Movies.id == movie_id))
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    await db.delete(movie)
    await db.commit()
    return {"message": "Movie deleted successfully."}
