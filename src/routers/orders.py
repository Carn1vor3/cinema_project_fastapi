from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.database import get_db
from src.dependencies import get_current_user, get_current_admin
from src.services.orders import (
    create_order_for_user,
    cancel_order_for_user,
    get_orders_for_user,
    get_all_orders,
)
from src.models.users import User
from src.schemas.orders import OrderSchema, CreateOrderResponse, CreateOrderRequest

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=CreateOrderResponse)
async def create_order(
    body: CreateOrderRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_order_for_user(current_user, db, movies_ids=body.movies_ids)


@router.get("/me", response_model=List[OrderSchema])
async def get_my_orders(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await get_orders_for_user(current_user, db)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = await cancel_order_for_user(order_id, db, current_user.id)
    return {"status": "success", "order_id": order.id, "new_status": order.status}


@router.get("/", response_model=List[OrderSchema])
async def admin_get_orders(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_admin),
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    orders = await get_all_orders(db, user_id, status, from_date, to_date)
    return orders
