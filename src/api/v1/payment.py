from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.auth import handle_api_key
from src.db.engine import get_session
from src.schemas.payment import (
    PaymentCreate,
    PaymentCreatedResponse,
    PaymentDetail,
)
from src.services.payment import PaymentService

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
        session: AsyncSession = Depends(get_session),
) -> PaymentCreatedResponse:
    service = PaymentService(session)
    payment = await service.create_payment(body, idempotency_key)

    return PaymentCreatedResponse(
        payment_id=payment.id,
        status=payment.status,
        created_at=payment.created_at,
    )


@router.get(
    path="/{payment_id}",
    response_model=PaymentDetail
)
async def get_payment(
        payment_id: UUID,
        session: AsyncSession = Depends(get_session),
) -> PaymentDetail:
    service = PaymentService(session)
    payment = await service.get_payment(payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return PaymentDetail.model_validate(payment)
