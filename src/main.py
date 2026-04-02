import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.payment import router as payments_router
from src.broker import broker
from src.workers.outbox import outbox_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    task = asyncio.create_task(outbox_worker())
    yield
    task.cancel()
    await broker.close()


app = FastAPI(lifespan=lifespan)
app.include_router(payments_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
