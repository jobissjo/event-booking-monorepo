from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token, oauth2_scheme
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine, get_db
from app.messaging.consumer import ActivityConsumer
from app.schemas.activity import ActivityResponse
from app.services.activity_service import ActivityService


consumer = ActivityConsumer(AsyncSessionLocal)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await consumer.start()
    yield
    await consumer.close()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="User-scoped activity feed service backed by RabbitMQ events.",
    lifespan=lifespan,
)


async def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    return decode_access_token(token)


def get_activity_service(db: AsyncSession = Depends(get_db)) -> ActivityService:
    return ActivityService(db)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get(
    "/api/activity-service/activities",
    response_model=list[ActivityResponse],
    tags=["Activities"],
)
async def list_my_activities(
    limit: int = 50,
    payload: dict = Depends(get_current_user_payload),
    service: ActivityService = Depends(get_activity_service),
):
    safe_limit = min(max(limit, 1), 100)
    return await service.list_for_user(user_id=payload["user_id"], limit=safe_limit)


@app.get(
    "/api/activity-service/activities/{activity_id}",
    response_model=ActivityResponse,
    tags=["Activities"],
)
async def get_my_activity(
    activity_id: UUID,
    payload: dict = Depends(get_current_user_payload),
    service: ActivityService = Depends(get_activity_service),
):
    activity = await service.get_for_user(activity_id=activity_id, user_id=payload["user_id"])
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity
