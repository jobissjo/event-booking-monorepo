from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func

from app.core.database_config import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(String, default="PENDING")
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
