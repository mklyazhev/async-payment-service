from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status
)

from src.core.auth import handle_api_key
from src.schemas.payment import (
    PaymentCreate,
    PaymentCreatedResponse,
    PaymentDetail,
    PaymentStatus,
)


router = APIRouter(
    prefix="/payments", 
    tags=["payments"],
    dependencies=[Depends(handle_api_key)],
)

IdempotencyKeyHeader = Annotated[str, Header(alias="Idempotency-Key")]


@router.post(
    path="/", 
    status_code=status.HTTP_202_ACCEPTED, 
    response_model=PaymentCreatedResponse
)
async def create_payment(
    idempotency_key: IdempotencyKeyHeader,
    body: PaymentCreate,
) -> PaymentCreatedResponse:
    return PaymentCreatedResponse(
        payment_id=uuid4(),
        status=PaymentStatus.pending,
        created_at=datetime.now(timezone.utc),
    )


@router.get(path="/{payment_id}", response_model=PaymentDetail)
async def get_payment(payment_id: UUID) -> PaymentDetail:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Payment not found",
    )
