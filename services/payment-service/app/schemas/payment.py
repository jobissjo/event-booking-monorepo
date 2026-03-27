from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, field_validator


AllowedPaymentStatus = Literal["PENDING", "SUCCEEDED", "FAILED"]


class PaymentIntentCreate(BaseModel):
    booking_id: int
    event_id: UUID
    user_id: int
    amount: Decimal
    currency: str = "INR"

    @field_validator("booking_id", "user_id")
    @classmethod
    def ids_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("amount must be greater than zero")
        return value

    @field_validator("currency")
    @classmethod
    def currency_must_be_iso_code(cls, value: str) -> str:
        normalized_value = value.strip().upper()
        if len(normalized_value) != 3:
            raise ValueError("currency must be a 3-letter ISO code")
        return normalized_value


class PaymentStatusUpdate(BaseModel):
    status: AllowedPaymentStatus


class PaymentResponse(BaseModel):
    id: UUID
    booking_id: int
    event_id: UUID
    user_id: int
    amount: Decimal
    currency: str
    status: AllowedPaymentStatus
    provider_reference: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
