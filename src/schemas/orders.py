from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from models.orders import OrderStatusEnum


class OrderCreateSchema(BaseModel):
    pass


class CreateOrderRequest(BaseModel):
    movies_ids: List[int]


class OrderItemSchema(BaseModel):
    movie_id: int
    price_at_order: Decimal

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: Decimal
    items: List[OrderItemSchema] = Field(default_factory=list)

    class Config:
        orm_mode = True


class OrderInfo(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: float


class CreateOrderResponse(BaseModel):
    message: str
    order: Optional[OrderInfo]
    ordered_movies: List[Dict]
