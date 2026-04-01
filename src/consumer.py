import asyncio
import logging
import random
from datetime import datetime, timezone

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType
from sqlalchemy import select

from src.common.config import get_settings
from src.common.constants import DLX_NAME, MAIN_EXCHANGE, DLQ_NAME, QUEUE_NAME
from src.common.enums import PaymentStatus
from src.db.engine import async_session_maker
from src.db.models.payment import Payment


logger = logging.getLogger(__name__)
settings = get_settings()

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

dlx = RabbitExchange(DLX_NAME, type=ExchangeType.DIRECT)
main_exchange = RabbitExchange(MAIN_EXCHANGE, type=ExchangeType.DIRECT)

dlq = RabbitQueue(
    DLQ_NAME,
    durable=True,
    routing_key=DLQ_NAME,
)

main_queue = RabbitQueue(
    QUEUE_NAME,
    durable=True,
    routing_key=QUEUE_NAME,
    arguments={
        "x-dead-letter-exchange": DLX_NAME,
        "x-dead-letter-routing-key": DLQ_NAME,
    },
)


@broker.subscriber(main_queue, exchange=main_exchange)
async def handle_payment(payload: dict) -> None:
    last_error: Exception | None = None

    for attempt in range(settings.max_consumer_retries):
        try:
            await process_payment(payload)
            return
        except Exception as e:  # pylint: disable=broad-except
            last_error = e
            logger.warning(
                "Attempt %d/%d failed: %s",
                attempt + 1,
                settings.max_consumer_retries,
                e,
            )
            if attempt < settings.max_consumer_retries - 1:
                await asyncio.sleep(2 ** attempt)

    logger.error(
        "Payment permanently failed after %d attempts: %s",
        settings.max_consumer_retries,
        last_error,
    )
    raise last_error


async def process_payment(payload: dict) -> None:
    payment_id = payload.get("payment_id")
    logger.info("Processing payment %s", payment_id)

    async with async_session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()

            if not payment:
                logger.error("Payment %s not found", payment_id)
                return

            success = await emulate_gateway()
            payment.status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED
            payment.processed_at = datetime.now(timezone.utc)

    await send_webhook(payment)
    logger.info("Payment %s processed: %s", payment_id, payment.status)


async def emulate_gateway() -> bool:
    await asyncio.sleep(random.uniform(2, 5))
    return random.random() < 0.9


async def send_webhook(payment: Payment) -> None:
    payload = {
        "payment_id": str(payment.id),
        "status": payment.status,
        "amount": str(payment.amount),
        "currency": payment.currency,
        "processed_at": payment.processed_at.isoformat(),
    }
    for attempt in range(settings.max_webhook_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    payment.webhook_url,
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                return
        except httpx.HTTPError as e:
            logger.error("Webhook attempt %d failed for %s: %s", attempt + 1, payment.id, e)
            if attempt < settings.max_webhook_retries - 1:
                await asyncio.sleep(2 ** attempt)

    logger.error("Webhook permanently failed for %s", payment.id)


@broker.subscriber(dlq, exchange=dlx)
async def handle_dead_letter(payload: dict) -> None:
    logger.error("Dead letter received: %s", payload)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(app.run())
