from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import AbstractBase
from src.common.enums import Currency, PaymentStatus


class Payment(AbstractBase):
    __tablename__ = "payments"

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(String(3), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    status: Mapped[PaymentStatus] = mapped_column(
        String(20),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    webhook_url: Mapped[str] = mapped_column(Text, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
