import json
from datetime import datetime, timezone

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from app.core.config import settings


async def publish_activity_event(
    *,
    user_id: int,
    message: str,
    source: str = "booking-service",
) -> None:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            settings.ACTIVITY_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )
        payload = {
            "user_id": user_id,
            "message": message,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await exchange.publish(
            Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=settings.ACTIVITY_ROUTING_KEY,
        )
    finally:
        await connection.close()
