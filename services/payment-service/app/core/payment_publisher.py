import json
from datetime import datetime, timezone
from uuid import UUID

import aio_pika
from aio_pika import DeliveryMode, ExchangeType, Message

from app.core.config import settings


async def publish_payment_event(
    *,
    payment_id: UUID,
    booking_id: int,
    status: str,
    routing_key: str,
) -> None:
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            settings.PAYMENT_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )
        payload = {
            "id": str(payment_id),
            "booking_id": booking_id,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await exchange.publish(
            Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
    finally:
        await connection.close()
