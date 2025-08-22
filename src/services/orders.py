from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from sqlalchemy.orm import selectinload

from models.orders import Orders, OrderItems, OrderStatusEnum
from models.users import User
from models.movies import Movies
from models.carts import Carts, CartItems
from schemas.orders import OrderSchema, OrderItemSchema
from services.email import send_order_confirmation_email


async def create_order_for_user(
    user: User, db: AsyncSession, movies_ids: list[int] | None = None
) -> dict:
    stmt = (
        select(Carts).options(selectinload(Carts.items)).where(Carts.user_id == user.id)
    )
    cart = (await db.execute(stmt)).scalar_one_or_none()

    if not cart or not cart.items:
        return {"message": "Cart is empty.", "order": None, "ordered_movies": []}

    if movies_ids:
        cart_movie_ids = [
            item.movie_id for item in cart.items if item.movie_id in movies_ids
        ]
    else:
        cart_movie_ids = [item.movie_id for item in cart.items]

    if not cart_movie_ids:
        return {
            "message": "No selected movies in the cart.",
            "order": None,
            "ordered_movies": [],
        }

    stmt = select(Movies).where(Movies.id.in_(cart_movie_ids))
    movies = (await db.execute(stmt)).scalars().all()
    available_movies = [m for m in movies if m.is_available]

    if not available_movies:
        return {
            "message": "No movies available for purchase.",
            "order": None,
            "ordered_movies": [],
        }

    stmt = (
        select(OrderItems.movie_id)
        .join(Orders)
        .where(
            and_(Orders.user_id == user.id, Orders.status == OrderStatusEnum.PENDING)
        )
    )
    pending_movies = (await db.execute(stmt)).scalars().all()

    movies_to_order = [m for m in available_movies if m.id not in pending_movies]
    if not movies_to_order:
        return {
            "message": "All selected movies are already in a pending order.",
            "order": None,
            "ordered_movies": [],
        }

    new_order = Orders(
        user_id=user.id, status=OrderStatusEnum.PENDING, created_at=datetime.utcnow()
    )
    db.add(new_order)
    await db.flush()

    items = [
        OrderItems(order_id=new_order.id, movie_id=m.id, price_at_order=m.price)
        for m in movies_to_order
    ]
    db.add_all(items)
    new_order.total_amount = sum(item.price_at_order for item in items)

    ordered_movie_ids = [m.id for m in movies_to_order]
    stmt = delete(CartItems).where(
        and_(CartItems.cart_id == cart.id, CartItems.movie_id.in_(ordered_movie_ids))
    )
    await db.execute(stmt)

    await db.commit()

    await send_order_confirmation_email(user.email, new_order.id)

    ordered_movies_info = [
        {"id": m.id, "name": m.name, "price": m.price} for m in movies_to_order
    ]

    return {
        "message": "Order created successfully.",
        "order": {
            "id": new_order.id,
            "user_id": new_order.user_id,
            "created_at": new_order.created_at,
            "status": new_order.status,
            "total_amount": new_order.total_amount,
        },
        "ordered_movies": ordered_movies_info,
    }


async def get_orders_for_user(user: User, db: AsyncSession) -> List[OrderSchema]:
    stmt = (
        select(Orders)
        .where(Orders.user_id == user.id)
        .options(selectinload(Orders.items))
        .order_by(Orders.created_at.desc())
    )
    result = await db.execute(stmt)
    orders = result.scalars().all()

    orders_data = []
    for order in orders:
        items = [
            OrderItemSchema(movie_id=item.movie_id, price_at_order=item.price_at_order)
            for item in order.items
        ]
        orders_data.append(
            OrderSchema(
                id=order.id,
                user_id=order.user_id,
                created_at=order.created_at,
                status=order.status.value,
                total_amount=order.total_amount or Decimal("0.00"),
                items=items,
            )
        )
    return orders_data


async def cancel_order_for_user(order_id: int, db: AsyncSession, current_user_id: int):
    result = await db.execute(
        select(Orders).where(Orders.id == order_id, Orders.user_id == current_user_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=400, detail="Only pending orders can be canceled"
        )

    order.status = OrderStatusEnum.CANCELED
    await db.commit()
    await db.refresh(order)
    return order


async def get_all_orders(
    db: AsyncSession,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[Orders]:
    filters = []

    if user_id:
        filters.append(Orders.user_id == user_id)
    if status:
        filters.append(Orders.status == status)
    if from_date:
        filters.append(Orders.created_at >= from_date)
    if to_date:
        filters.append(Orders.created_at <= to_date)

    stmt = select(Orders).options(selectinload(Orders.items))
    if filters:
        stmt = stmt.where(and_(*filters))

    result = await db.execute(stmt)
    return result.scalars().all()
