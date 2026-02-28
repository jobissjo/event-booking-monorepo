from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.db import init_db, close_db
from app.core.exceptions import AppException, app_exception_handler
from app.core.config import settings
from app.routes.event import router as event_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Event & Venue management service. Only organizers and admins can create events and venues.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(event_router, prefix="/api/events-service", tags=["Events & Venues"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
