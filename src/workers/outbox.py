import asyncio
import logging

from sqlalchemy import select

from src.broker import broker
from src.common.enums import OutboxStatus
from src.db.engine import async_session_maker
from src.db.models.outbox import Outbox

logger = logging.getLogger(__name__)


async def process_outbox() -> None:
    async with async_session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Outbox)
                .where(Outbox.status == OutboxStatus.NEW)
                .with_for_update(skip_locked=True)
                .limit(10)
            )
            events = result.scalars().all()

            for event in events:
                try:
                    await broker.publish(
                        event.payload,
                        routing_key=event.routing_key,
                    )
                    event.status = OutboxStatus.PUBLISHED
                except Exception as e:
                    logger.error(f"Failed to publish outbox event {event.id}: {e}")


async def outbox_worker() -> None:
    logger.info("Outbox worker started")
    while True:
        try:
            await process_outbox()
        except Exception as e:
            logger.error(f"Outbox worker error: {e}")
        await asyncio.sleep(1)
