import asyncio
import json
import logging

import aio_pika
from aio_pika import ExchangeType, IncomingMessage
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import settings
from app.schemas.activity_event import ActivityEvent
from app.services.activity_service import ActivityService


class ActivityConsumer:
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self.session_factory = session_factory
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.abc.AbstractRobustChannel | None = None

    async def start(self) -> None:
        retries = settings.RABBITMQ_CONNECT_RETRIES
        delay = settings.RABBITMQ_CONNECT_DELAY_SECONDS
        for attempt in range(1, retries + 1):
            try:
                self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                break
            except Exception as exc:
                logging.warning(
                    "[ActivityConsumer] RabbitMQ not ready (attempt %d/%d): %s",
                    attempt,
                    retries,
                    exc,
                )
                if attempt == retries:
                    raise
                await asyncio.sleep(delay)

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=20)

        exchange = await self.channel.declare_exchange(
            settings.ACTIVITY_EXCHANGE,
            ExchangeType.TOPIC,
            durable=True,
        )
        queue = await self.channel.declare_queue(settings.ACTIVITY_QUEUE, durable=True)
        await queue.bind(exchange, routing_key=settings.ACTIVITY_ROUTING_KEY)
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
                activity_event = ActivityEvent.model_validate(payload)
            except (json.JSONDecodeError, ValidationError):
                return

            async with self.session_factory() as db:
                service = ActivityService(db)
                await service.create_from_event(activity_event)
