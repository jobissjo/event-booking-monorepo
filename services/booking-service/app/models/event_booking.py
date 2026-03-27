from sqlalchemy import Column, DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database_config import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(Integer, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="INR")
    payment_id = Column(UUID(as_uuid=True), nullable=True)
    payment_status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("event_id", "seat_number", name="unique_seat_per_event"),
    )
