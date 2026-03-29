from uuid import uuid4

from fastapi.testclient import TestClient


def _valid_payment_json() -> dict:
    return {
        "amount": "999.99",
        "currency": "RUB",
        "description": "test",
        "metadata": {"order_id": "123"},
        "webhook_url": "https://example.com/hook",
    }


def test_create_payment_401_without_api_key(client: TestClient) -> None:
    r = client.post(
        "/api/v1/payments/",
        json=_valid_payment_json(),
        headers={
            "Idempotency-Key": "key-1",
        },
    )
    assert r.status_code == 401


def test_create_payment_401_wrong_api_key(client: TestClient) -> None:
    r = client.post(
        "/api/v1/payments/",
        json=_valid_payment_json(),
        headers={
            "X-API-Key": "wrong-key",
            "Idempotency-Key": "key-1",
        },
    )
    assert r.status_code == 401


def test_create_payment_422_without_idempotency_key(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    r = client.post(
        "/api/v1/payments/",
        json=_valid_payment_json(),
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_create_payment_202(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    headers = {
        **auth_headers,
        "Idempotency-Key": "key-1",
    }
    r = client.post(
        "/api/v1/payments/",
        json=_valid_payment_json(),
        headers=headers,
    )
    assert r.status_code == 202
    data = r.json()
    assert "payment_id" in data
    assert data["status"] == "pending"
    assert "created_at" in data


def test_get_payment_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    pid = str(uuid4())
    r = client.get(f"/api/v1/payments/{pid}", headers=auth_headers)
    assert r.status_code == 404
