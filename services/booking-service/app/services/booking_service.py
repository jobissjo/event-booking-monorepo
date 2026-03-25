from typing import Optional

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.event_booking import Booking
from app.schemas.booking import BookingCreate, BookingStatusUpdate


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(self, booking_in: BookingCreate) -> Booking:
        booking = Booking(
            event_id=booking_in.event_id,
            user_id=booking_in.user_id,
            seat_number=booking_in.seat_number,
            status="PENDING",
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
        return booking

    async def get_booking(self, booking_id: int) -> Booking:
        booking = await self.db.get(Booking, booking_id)
        if booking is None:
            raise AppException(status_code=404, detail="Booking not found")
        return booking

    async def list_bookings(
        self,
        event_id: Optional[int] = None,
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
        return booking

    async def delete_booking(self, booking_id: int) -> dict:
        booking = await self.get_booking(booking_id)
        await self.db.delete(booking)
        await self.db.commit()
        return {"detail": "Booking deleted successfully"}
