from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.activity_publisher import publish_activity_event
from app.core.exceptions import AppException
from app.core.payment_client import PaymentClient, PaymentClientError
from app.models.event_booking import Booking
from app.schemas.booking import BookingCreate, BookingStatusUpdate


class BookingService:
    def __init__(self, db: AsyncSession, payment_client: PaymentClient | None = None):
        self.db = db
        self.payment_client = payment_client or PaymentClient()

    async def create_booking(self, booking_in: BookingCreate) -> Booking:
        booking = Booking(
            event_id=booking_in.event_id,
            user_id=booking_in.user_id,
            seat_number=booking_in.seat_number,
            status="PENDING",
            amount=booking_in.amount,
            currency=booking_in.currency,
            payment_status="PENDING",
        )
        self.db.add(booking)

        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise AppException(
                status_code=409,
                detail="This seat is already booked for the selected event",
            ) from exc

        await self.db.refresh(booking)
        await self._create_payment_for_booking(booking)
        await self._publish_activity(
            user_id=booking.user_id,
            message=f"Created booking for event {booking.event_id}, seat {booking.seat_number}.",
        )
        return booking

    async def get_booking(self, booking_id: int) -> Booking:
        booking = await self.db.get(Booking, booking_id)
        if booking is None:
            raise AppException(status_code=404, detail="Booking not found")
        return booking

    async def list_bookings(
        self,
        event_id: Optional[UUID] = None,
        user_id: Optional[int] = None,
    ) -> list[Booking]:
        query: Select[tuple[Booking]] = select(Booking)

        if event_id is not None:
            query = query.where(Booking.event_id == event_id)
        if user_id is not None:
            query = query.where(Booking.user_id == user_id)

        query = query.order_by(Booking.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_booking_status(
        self,
        booking_id: int,
        status_in: BookingStatusUpdate,
    ) -> Booking:
        booking = await self.get_booking(booking_id)
        booking.status = status_in.status
        await self.db.commit()
        await self.db.refresh(booking)
        await self._publish_activity(
            user_id=booking.user_id,
            message=f"Booking {booking.id} status changed to {booking.status}.",
        )
        return booking

    async def delete_booking(self, booking_id: int) -> dict:
        booking = await self.get_booking(booking_id)
        user_id = booking.user_id
        message = f"Deleted booking {booking.id} for event {booking.event_id}."
        await self.db.delete(booking)
        await self.db.commit()
        await self._publish_activity(user_id=user_id, message=message)
        return {"detail": "Booking deleted successfully"}

    async def sync_payment_status(
        self,
        *,
        booking_id: int,
        payment_id: UUID,
        payment_status: str,
    ) -> Booking | None:
        booking = await self.db.get(Booking, booking_id)
        if booking is None:
            return None

        booking.payment_id = payment_id
        booking.payment_status = payment_status
        if payment_status == "SUCCEEDED":
            booking.status = "CONFIRMED"
        elif payment_status == "FAILED":
            booking.status = "CANCELLED"

        await self.db.commit()
        await self.db.refresh(booking)
        await self._publish_activity(
            user_id=booking.user_id,
            message=f"Payment for booking {booking.id} changed to {payment_status}.",
        )
        return booking

    async def _publish_activity(self, *, user_id: int, message: str) -> None:
        try:
            await publish_activity_event(user_id=user_id, message=message)
        except Exception as exc:
            print(f"Failed to publish activity event: {exc}")

    async def _create_payment_for_booking(self, booking: Booking) -> None:
        try:
            payment = await self.payment_client.create_payment_intent(
                booking_id=booking.id,
                event_id=booking.event_id,
                user_id=booking.user_id,
                amount=Decimal(str(booking.amount)),
                currency=booking.currency,
            )
        except PaymentClientError:
            booking.payment_status = "INITIATION_FAILED"
            await self.db.commit()
            await self.db.refresh(booking)
            return

        booking.payment_id = UUID(payment["id"])
        booking.payment_status = payment["status"]
        await self.db.commit()
        await self.db.refresh(booking)
