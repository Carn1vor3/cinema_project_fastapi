from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, UTC

from sqlalchemy.orm import selectinload

from src.models.carts import Carts, CartItems
from src.models.movies import Movies


async def add_movie_to_cart(db: AsyncSession, user_id: int, movie_id: int):
    cart = await db.scalar(select(Carts).where(Carts.user_id == user_id))
    if not cart:
        cart = Carts(user_id=user_id)
        db.add(cart)
        await db.flush()

    existing_item = await db.scalar(
        select(CartItems).where(
            CartItems.cart_id == cart.id, CartItems.movie_id == movie_id
        )
    )
    if existing_item:
        raise HTTPException(status_code=400, detail="Movie already in your cart.")

    item = CartItems(cart_id=cart.id, movie_id=movie_id, added_at=datetime.now(UTC))
    db.add(item)
    await db.commit()
    return item


async def remove_movie_from_cart(db: AsyncSession, user_id: int, movie_id: int):
    cart = await db.scalar(select(Carts).where(Carts.user_id == user_id))
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


async def get_cart_items(db: AsyncSession, user_id: int):
    cart = await db.scalar(
        select(Carts)
        .where(Carts.user_id == user_id)
        .options(selectinload(Carts.items).selectinload(CartItems.movie))
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


async def clear_cart(db: AsyncSession, user_id: int):
    cart = await db.scalar(select(Carts).where(Carts.user_id == user_id))
    if not cart:
        return {"message": "Cart is already empty."}

    await db.execute(delete(CartItems).where(CartItems.cart_id == cart.id))
    await db.commit()
    return {"message": "Cart cleared."}


async def get_user_cart_for_admin(db: AsyncSession, user_id: int):
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
