from datetime import datetime

from pydantic import BaseModel, field_validator


class ActivityEvent(BaseModel):
    user_id: int
    message: str
    source: str | None = None
    created_at: datetime | None = None

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("user_id must be a positive integer")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("message must not be blank")
        return normalized_value
