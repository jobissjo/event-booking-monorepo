from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import AppException, app_exception_handler
from app.routes.payment import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Payment intent and payment status service for bookings.",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(payment_router, prefix="/api/payments-service", tags=["Payments"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
