import secrets

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from src.common.config import get_settings


api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


def _raise_unauthorized() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key",
    )


async def handle_api_key(key: str | None = Security(api_key)) -> str:
    if not key:
        _raise_unauthorized()

    expected = get_settings().api_key
    try:
        if not secrets.compare_digest(key, expected):
            _raise_unauthorized()
    except (TypeError, ValueError):
        _raise_unauthorized()

    return key
