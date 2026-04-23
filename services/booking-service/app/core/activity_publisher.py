import asyncio
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
    connection = None
    retries = settings.RABBITMQ_CONNECT_RETRIES
    delay = settings.RABBITMQ_CONNECT_DELAY_SECONDS
    for attempt in range(1, retries + 1):
        try:
            connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            break
        except Exception:
            if attempt == retries:
                raise
            await asyncio.sleep(delay)
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
        if connection is not None:
            await connection.close()
