from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


NotificationType = Literal[
    "BOOKING_CREATED",
    "BOOKING_CONFIRMED",
    "BOOKING_CANCELLED",
    "REMINDER",
    "SYSTEM",
]
NotificationChannel = Literal["IN_APP", "EMAIL", "SMS", "PUSH"]


class NotificationCreate(BaseModel):
    user_id: int
    recipient_email: str | None = None
    event_id: int | None = None
    booking_id: int | None = None
    notification_type: NotificationType = Field(alias="type")
    channel: NotificationChannel = "IN_APP"
    title: str
    message: str
    payload: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("user_id", "event_id", "booking_id")
    @classmethod
    def validate_positive_ids(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("title", "message")
    @classmethod
    def validate_non_blank_text(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("must not be blank")
        return normalized_value


class BookingNotificationCreate(BaseModel):
    booking_id: int
    user_id: int
    event_id: int
    seat_number: str
    status: Literal["PENDING", "CONFIRMED", "CANCELLED"] = "PENDING"
    recipient_email: str | None = None

    @field_validator("booking_id", "user_id", "event_id")
    @classmethod
    def validate_positive_ids(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value

    @field_validator("seat_number")
    @classmethod
    def validate_seat_number(cls, value: str) -> str:
        normalized_value = value.strip().upper()
        if not normalized_value:
            raise ValueError("seat_number must not be blank")
        return normalized_value


class NotificationListFilters(BaseModel):
    user_id: int | None = None
    event_id: int | None = None
    booking_id: int | None = None
    is_read: bool | None = None
    notification_type: NotificationType | None = Field(default=None, alias="type")
    channel: NotificationChannel | None = None

    model_config = ConfigDict(populate_by_name=True)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    recipient_email: str | None
    event_id: int | None
    booking_id: int | None
    notification_type: NotificationType = Field(alias="type")
    channel: NotificationChannel
    title: str
    message: str
    payload: dict[str, Any] | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
