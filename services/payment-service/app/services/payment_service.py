from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.core.payment_publisher import publish_payment_event
from app.models.payment import Payment
from app.schemas.payment import PaymentIntentCreate, PaymentStatusUpdate


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_intent(self, payment_in: PaymentIntentCreate) -> Payment:
        idempotency_key = f"booking:{payment_in.booking_id}"
        existing = await self._get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing

        payment = Payment(
            booking_id=payment_in.booking_id,
            event_id=payment_in.event_id,
            user_id=payment_in.user_id,
            amount=payment_in.amount,
            currency=payment_in.currency,
            status="PENDING",
            provider_reference=f"demo_{uuid4().hex[:16]}",
            idempotency_key=idempotency_key,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        await self._publish_status(payment, routing_key="payment.created")
        return payment

    async def get_payment(self, payment_id: UUID) -> Payment:
        payment = await self.db.get(Payment, payment_id)
        if payment is None:
            raise AppException(status_code=404, detail="Payment not found")
        return payment

    async def update_payment_status(
        self,
        payment_id: UUID,
        status_in: PaymentStatusUpdate,
    ) -> Payment:
        payment = await self.get_payment(payment_id)
        payment.status = status_in.status
        await self.db.commit()
        await self.db.refresh(payment)

        routing_key = "payment.succeeded" if payment.status == "SUCCEEDED" else "payment.failed"
        await self._publish_status(payment, routing_key=routing_key)
        return payment

    async def _get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def _publish_status(self, payment: Payment, *, routing_key: str) -> None:
        try:
            await publish_payment_event(
                payment_id=payment.id,
                booking_id=payment.booking_id,
                status=payment.status,
                routing_key=routing_key,
            )
        except Exception as exc:
            print(f"Failed to publish payment event: {exc}")
