import json
from uuid import UUID

import aio_pika
from aio_pika import ExchangeType, IncomingMessage
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.services.booking_service import BookingService


class PaymentEvent(BaseModel):
    id: UUID
    booking_id: int
    status: str


class PaymentConsumer:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractRobustChannel | None = None

    async def start(self) -> None:
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=20)

        exchange = await self.channel.declare_exchange(
            settings.PAYMENT_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )
        queue = await self.channel.declare_queue(settings.PAYMENT_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=settings.PAYMENT_ROUTING_KEY)
        await queue.consume(self._handle_message)

    async def close(self) -> None:
        if self.channel is not None and not self.channel.is_closed:
            await self.channel.close()
        if self.connection is not None and not self.connection.is_closed:
            await self.connection.close()

    async def _handle_message(self, message: IncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                payload = json.loads(message.body.decode("utf-8"))
                payment_event = PaymentEvent.model_validate(payload)
            except (json.JSONDecodeError, ValidationError):
                return

            async with self.session_factory() as db:
                service = BookingService(db)
                await service.sync_payment_status(
                    booking_id=payment_event.booking_id,
                    payment_id=payment_event.id,
                    payment_status=payment_event.status,
                )
