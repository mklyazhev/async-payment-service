from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.payment import Payment
from src.db.models.outbox import Outbox
from src.common.enums import PaymentStatus, OutboxStatus
from src.repositories.payment import PaymentRepository
from src.schemas.payment import PaymentCreate
from src.common.constants import QUEUE_NAME, EVENT_PAYMENT_CREATED


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PaymentRepository(session)

    async def create_payment(
            self,
            data: PaymentCreate,
            idempotency_key: str,
    ) -> Payment:
        existing = await self.repo.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing

        payment = Payment(
            id=uuid4(),
            amount=data.amount,
            currency=data.currency,
            description=data.description,
            payment_metadata=data.payment_metadata,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            webhook_url=str(data.webhook_url),
        )

        outbox = Outbox(
            id=uuid4(),
            event_type=EVENT_PAYMENT_CREATED,
            payload={"payment_id": str(payment.id)},
            routing_key=QUEUE_NAME,
            status=OutboxStatus.NEW,
        )

        await self.repo.create(payment)
        self.session.add(outbox)
        await self.session.commit()

        return payment

    async def get_payment(self, payment_id) -> Payment | None:
        return await self.repo.get_by_id(payment_id)
