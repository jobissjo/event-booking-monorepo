import uuid

from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(Integer, nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    provider_reference = Column(String(64), nullable=False, unique=True)
    idempotency_key = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
