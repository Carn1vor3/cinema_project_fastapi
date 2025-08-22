from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import HTMLResponse

from database import get_db
from models.payment import Payments
from services.payments import get_payments_history, create_checkout_session
from models.users import User
from schemas.payments import PaymentSchema, PaymentConfirmRequest
from services.users import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout/{order_id}", response_model=dict)
async def checkout_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        success_url = "http://localhost:8000/payments/success"
        cancel_url = "http://localhost:8000/payments/cancel"

        session_info = await create_checkout_session(
            current_user, order_id, db, success_url, cancel_url
        )
        return session_info
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history", response_model=List[PaymentSchema])
async def payments_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    payments = await get_payments_history(current_user.id, db)
    return payments


@router.get("/success", response_class=HTMLResponse)
async def payment_success():
    return "<h2>Payment Successful! ✅</h2>"


@router.get("/cancel", response_class=HTMLResponse)
async def payment_cancel():
    return "<h2>Payment Cancelled ❌</h2>"
