from datetime import timezone
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.schemas.activity_event import ActivityEvent


class ActivityService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_from_event(self, event: ActivityEvent) -> Activity:
        activity = Activity(
            user_id=event.user_id,
            message=event.message,
        )
        if event.created_at is not None:
            activity.created_at = event.created_at.astimezone(timezone.utc)

        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def list_for_user(self, user_id: int, limit: int = 50) -> list[Activity]:
        query: Select[tuple[Activity]] = (
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(Activity.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_for_user(self, activity_id: UUID, user_id: int) -> Activity | None:
        query: Select[tuple[Activity]] = select(Activity).where(
            Activity.id == activity_id,
            Activity.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
