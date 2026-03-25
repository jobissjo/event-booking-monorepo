from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


AllowedBookingStatus = Literal["PENDING", "CONFIRMED", "CANCELLED"]


class BookingCreate(BaseModel):
    event_id: int
    user_id: int
    seat_number: str

    @field_validator("event_id", "user_id")
    @classmethod
    def ids_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("seat_number")
    @classmethod
    def seat_number_must_not_be_blank(cls, value: str) -> str:
        normalized_value = value.strip().upper()
        if not normalized_value:
            raise ValueError("seat_number must not be blank")
        return normalized_value


class BookingStatusUpdate(BaseModel):
    status: AllowedBookingStatus


class BookingResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    seat_number: str
    status: AllowedBookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
