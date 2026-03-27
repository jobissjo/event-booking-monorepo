from decimal import Decimal
from uuid import UUID

import httpx

from app.core.config import settings


class PaymentClientError(Exception):
    pass


class PaymentClient:
    async def create_payment_intent(
        self,
        *,
        booking_id: int,
        event_id: UUID,
        user_id: int,
        amount: Decimal,
        currency: str,
    ) -> dict:
        payload = {
            "booking_id": booking_id,
            "event_id": str(event_id),
            "user_id": user_id,
            "amount": str(amount),
            "currency": currency,
        }

        async with httpx.AsyncClient(
            base_url=settings.PAYMENT_SERVICE_URL,
            timeout=settings.PAYMENT_TIMEOUT_SECONDS,
        ) as client:
            response = await client.post(
                "/api/payments-service/payments/intents",
                json=payload,
            )

        if response.status_code >= 400:
            raise PaymentClientError(response.text)

        return response.json()
