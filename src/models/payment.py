import enum
from datetime import datetime, UTC
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.database import Base
from src.models.users import User

if TYPE_CHECKING:
    from src.models.orders import Orders, OrderItems


class StatusEnum(str, enum.Enum):
    SUCCESSFUL = "successful"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="payments")

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    order: Mapped["Orders"] = relationship("Orders", back_populates="payments")

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(UTC)
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.CANCELED, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    external_payment_id: Mapped[str] = mapped_column(nullable=True)

    payment_items: Mapped[list["PaymentItems"]] = relationship(
        "PaymentItems", back_populates="payments"
    )


class PaymentItems(Base):
    __tablename__ = "payment_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), nullable=False)
    payments: Mapped["Payments"] = relationship(
        "Payments", back_populates="payment_items"
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id"), nullable=False
    )
    order_items: Mapped["OrderItems"] = relationship(
        "OrderItems", back_populates="payment_items"
    )

    price_at_payment: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
