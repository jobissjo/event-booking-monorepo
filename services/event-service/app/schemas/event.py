from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


# ─────────────────────── Venue Schemas ───────────────────────

class VenueCreate(BaseModel):
    name: str
    location: str
    capacity: int

    @field_validator("capacity")
    @classmethod
    def capacity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("capacity must be a positive integer")
        return v


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None


class VenueResponse(BaseModel):
    id: UUID
    name: str
    location: str
    capacity: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────── Event Schemas ───────────────────────

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    total_seats: int
    venue_id: UUID

    @field_validator("total_seats")
    @classmethod
    def seats_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("total_seats must be a positive integer")
        return v

    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_seats: Optional[int] = None
    venue_id: Optional[UUID] = None
    status: Optional[str] = None


class EventResponse(BaseModel):
    id: UUID
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    total_seats: int
    available_seats: int
    status: str
    venue: VenueResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
