import asyncio
import json

from robyn import Request, Robyn, SSEMessage, SSEResponse

from app.core.auth import AuthError, decode_access_token, require_authenticated_request
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.schemas.notification import BookingNotificationCreate, NotificationCreate
from app.services.notification_service import NotificationService, notification_hub


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

app = Robyn(__file__)


def _auth_error_response(detail: str) -> tuple[dict, int]:
    return {"detail": detail}, 401


def _not_found_response(detail: str) -> tuple[dict, int]:
    return {"detail": detail}, 404


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.post("/api/notifications-service/notifications")
async def create_notification(request: Request, notification_in: NotificationCreate):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notification = await service.create_notification(notification_in)
        return service.serialize_notification(notification)


@app.post("/api/notifications-service/notifications/from-booking")
async def create_booking_notification(
    request: Request,
    booking_notification: BookingNotificationCreate,
):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notification = await service.create_booking_notification(booking_notification)
        return service.serialize_notification(notification)


@app.get("/api/notifications-service/notifications")
async def list_notifications(
    request: Request,
    user_id: int | None = None,
    event_id: int | None = None,
    booking_id: int | None = None,
    is_read: bool | None = None,
    type: str | None = None,
    channel: str | None = None,
):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notifications = await service.list_notifications(
            user_id=user_id,
            event_id=event_id,
            booking_id=booking_id,
            is_read=is_read,
            notification_type=type,
            channel=channel,
        )
        return [service.serialize_notification(notification) for notification in notifications]


@app.get("/api/notifications-service/notifications/:notification_id")
async def get_notification(request: Request, notification_id: int):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notification = await service.get_notification(notification_id)
        if notification is None:
            return _not_found_response("Notification not found")
        return service.serialize_notification(notification)


@app.patch("/api/notifications-service/notifications/:notification_id/read")
async def mark_notification_as_read(request: Request, notification_id: int):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notification = await service.mark_as_read(notification_id)
        if notification is None:
            return _not_found_response("Notification not found")
        return service.serialize_notification(notification)


@app.patch("/api/notifications-service/notifications/read-all")
async def mark_all_notifications_as_read(request: Request, user_id: int):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    async with AsyncSessionLocal() as db:
        service = NotificationService(db)
        notifications = await service.mark_all_as_read(user_id)
        return [service.serialize_notification(notification) for notification in notifications]


@app.get("/api/notifications-service/stream")
async def notification_stream(request: Request, user_id: int):
    try:
        require_authenticated_request(request)
    except AuthError as exc:
        return _auth_error_response(str(exc))

    queue = notification_hub.subscribe_sse(user_id)

    async def event_generator():
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield SSEMessage("keep-alive", event="heartbeat")
                    continue

                yield SSEMessage(
                    json.dumps(payload),
                    event="notification",
                    id=str(payload["id"]),
                )
        finally:
            notification_hub.unsubscribe_sse(user_id, queue)

    return SSEResponse(event_generator())


@app.websocket("/api/notifications-service/ws")
async def notification_socket(websocket, user_id: int, token: str):
    try:
        decode_access_token(token)
    except AuthError:
        await websocket.send_json({"detail": "Could not validate credentials"})
        await websocket.close()
        return

    notification_hub.register_websocket(user_id, websocket)
    await websocket.send_json(
        {
            "detail": "Connected to notification stream",
            "user_id": user_id,
        }
    )

    try:
        while True:
            message = await websocket.receive_text()
            if message.lower() == "ping":
                await websocket.send_text("pong")
            else:
                await websocket.send_json(
                    {
                        "detail": "Notification socket is active",
                        "echo": message,
                    }
                )
    finally:
        notification_hub.unregister_websocket(websocket.id)


if __name__ == "__main__":
    asyncio.run(initialize_database())
    app.start(host=settings.HOST, port=settings.PORT)
