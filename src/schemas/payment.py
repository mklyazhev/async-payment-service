from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field

from src.common.enums import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: Currency
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    webhook_url: AnyUrl


class PaymentCreatedResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentDetail(BaseModel):
    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict
    status: PaymentStatus
    idempotency_key: str
    webhook_url: AnyUrl
    created_at: datetime
    processed_at: datetime | None
