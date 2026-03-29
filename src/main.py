from fastapi import FastAPI

from src.api.v1.payment import router as payments_router


app = FastAPI()
app.include_router(payments_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
