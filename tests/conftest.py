import os
os.environ.setdefault("API_KEY", "valid-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def api_key() -> str:
    return os.environ["API_KEY"]


@pytest.fixture
def auth_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key}


@pytest.fixture
def mock_payment():
    payment = MagicMock()
    payment.id = uuid4()
    payment.status = "pending"
    payment.amount = "999.99"
    payment.currency = "RUB"
    payment.description = "test"
    payment.payment_metadata = {"order_id": "123"}
    payment.idempotency_key = "key-1"
    payment.webhook_url = "https://example.com/hook"
    payment.created_at = datetime.now(timezone.utc)
    payment.processed_at = None
    return payment
