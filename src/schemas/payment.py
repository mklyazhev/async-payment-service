from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, BaseModel, Field, ConfigDict

from src.common.enums import Currency, PaymentStatus


class PaymentCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: Decimal = Field(gt=0)
    currency: Currency
    description: str
    payment_metadata: dict[str, Any] = Field(alias="metadata", default_factory=dict)
    webhook_url: AnyUrl


class PaymentCreatedResponse(BaseModel):
    payment_id: UUID
    status: PaymentStatus
    created_at: datetime


class PaymentDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    amount: Decimal
    currency: Currency
    description: str
    payment_metadata: dict[str, Any] = Field(
        alias="metadata",
        validation_alias="payment_metadata",
        default_factory=dict,
    )
    status: PaymentStatus
    idempotency_key: str
    webhook_url: AnyUrl
    created_at: datetime
    processed_at: datetime | None
