from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import AbstractBase
from src.common.enums import OutboxStatus


class Outbox(AbstractBase):
    __tablename__ = "outbox"
    __table_args__ = (
        Index("ix_outbox_status_next_retry", "status", "next_retry_at"),
    )

    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    routing_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(
        String(20),
        nullable=False,
        default=OutboxStatus.NEW
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
