import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import BookingNotificationCreate, NotificationCreate


class NotificationHub:
    def __init__(self) -> None:
        self._sse_subscribers: dict[int, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)
        self._websocket_subscribers: dict[str, dict[str, Any]] = {}

    def subscribe_sse(self, user_id: int) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._sse_subscribers[user_id].add(queue)
        return queue

    def unsubscribe_sse(self, user_id: int, queue: asyncio.Queue[dict[str, Any]]) -> None:
        subscribers = self._sse_subscribers.get(user_id)
        if not subscribers:
            return

        subscribers.discard(queue)
        if not subscribers:
            self._sse_subscribers.pop(user_id, None)

    def register_websocket(self, user_id: int, websocket: Any) -> None:
        self._websocket_subscribers[websocket.id] = {
            "user_id": user_id,
            "websocket": websocket,
        }

    def unregister_websocket(self, websocket_id: str) -> None:
        self._websocket_subscribers.pop(websocket_id, None)

    async def publish(self, user_id: int, payload: dict[str, Any]) -> None:
        for queue in list(self._sse_subscribers.get(user_id, set())):
            await queue.put(payload)

        stale_ids: list[str] = []
        for websocket_id, subscriber in self._websocket_subscribers.items():
            if subscriber["user_id"] != user_id:
                continue

            try:
                await subscriber["websocket"].send_json(payload)
            except Exception:
                stale_ids.append(websocket_id)

        for websocket_id in stale_ids:
            self.unregister_websocket(websocket_id)


notification_hub = NotificationHub()


class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_notification(self, notification_in: NotificationCreate) -> Notification:
        notification = Notification(
            user_id=notification_in.user_id,
            recipient_email=notification_in.recipient_email,
            event_id=notification_in.event_id,
            booking_id=notification_in.booking_id,
            notification_type=notification_in.notification_type,
            channel=notification_in.channel,
            title=notification_in.title,
            message=notification_in.message,
            payload=notification_in.payload,
            is_read=False,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        await notification_hub.publish(
            notification.user_id,
            self.serialize_notification(notification),
        )
        return notification

    async def create_booking_notification(
        self,
        booking_in: BookingNotificationCreate,
    ) -> Notification:
        status_to_type = {
            "PENDING": "BOOKING_CREATED",
            "CONFIRMED": "BOOKING_CONFIRMED",
            "CANCELLED": "BOOKING_CANCELLED",
        }
        status_to_title = {
            "PENDING": "Booking received",
            "CONFIRMED": "Booking confirmed",
            "CANCELLED": "Booking cancelled",
        }
        status_to_message = {
            "PENDING": f"Your booking for seat {booking_in.seat_number} is pending review.",
            "CONFIRMED": f"Your booking for seat {booking_in.seat_number} has been confirmed.",
            "CANCELLED": f"Your booking for seat {booking_in.seat_number} has been cancelled.",
        }

        return await self.create_notification(
            NotificationCreate(
                user_id=booking_in.user_id,
                recipient_email=booking_in.recipient_email,
                event_id=booking_in.event_id,
                booking_id=booking_in.booking_id,
                type=status_to_type[booking_in.status],
                channel="IN_APP",
                title=status_to_title[booking_in.status],
                message=status_to_message[booking_in.status],
                payload={
                    "booking_id": booking_in.booking_id,
                    "event_id": booking_in.event_id,
                    "seat_number": booking_in.seat_number,
                    "status": booking_in.status,
                },
            )
        )

    async def get_notification(self, notification_id: int) -> Notification | None:
        return await self.db.get(Notification, notification_id)

    async def list_notifications(
        self,
        user_id: int | None = None,
        event_id: int | None = None,
        booking_id: int | None = None,
        is_read: bool | None = None,
        notification_type: str | None = None,
        channel: str | None = None,
    ) -> list[Notification]:
        query: Select[tuple[Notification]] = select(Notification)

        if user_id is not None:
            query = query.where(Notification.user_id == user_id)
        if event_id is not None:
            query = query.where(Notification.event_id == event_id)
        if booking_id is not None:
            query = query.where(Notification.booking_id == booking_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        if notification_type is not None:
            query = query.where(Notification.notification_type == notification_type)
        if channel is not None:
            query = query.where(Notification.channel == channel)

        query = query.order_by(Notification.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: int) -> Notification | None:
        notification = await self.get_notification(notification_id)
        if notification is None:
            return None

        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_all_as_read(self, user_id: int) -> list[Notification]:
        notifications = await self.list_notifications(user_id=user_id, is_read=False)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)

        await self.db.commit()

        for notification in notifications:
            await self.db.refresh(notification)

        return notifications

    @staticmethod
    def serialize_notification(notification: Notification) -> dict[str, Any]:
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "recipient_email": notification.recipient_email,
            "event_id": notification.event_id,
            "booking_id": notification.booking_id,
            "type": notification.notification_type,
            "channel": notification.channel,
            "title": notification.title,
            "message": notification.message,
            "payload": notification.payload,
            "is_read": notification.is_read,
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "created_at": notification.created_at.isoformat(),
            "updated_at": notification.updated_at.isoformat(),
        }
