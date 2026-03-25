from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database_config import Base, engine
from app.core.exceptions import AppException, app_exception_handler
from app.core.config import settings
from app.routes.booking import router as booking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Booking management service for event seat reservations.",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(booking_router, prefix="/api/bookings-service", tags=["Bookings"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
