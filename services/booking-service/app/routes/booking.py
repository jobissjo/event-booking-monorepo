from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database_config import get_db
from app.core.deps import require_any_authenticated
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate
from app.services.booking_service import BookingService


router = APIRouter()


def get_booking_service(db: AsyncSession = Depends(get_db)) -> BookingService:
    return BookingService(db)


@router.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(
    booking_in: BookingCreate,
    _payload=Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
):
    return await service.create_booking(booking_in)


@router.get("/bookings", response_model=List[BookingResponse])
async def list_bookings(
    event_id: Optional[int] = Query(default=None),
    user_id: Optional[int] = Query(default=None),
    _payload=Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
):
    return await service.list_bookings(event_id=event_id, user_id=user_id)


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    _payload=Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
):
    return await service.get_booking(booking_id)


@router.patch("/bookings/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    status_in: BookingStatusUpdate,
    _payload=Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
):
    return await service.update_booking_status(booking_id, status_in)


@router.delete("/bookings/{booking_id}")
async def delete_booking(
    booking_id: int,
    _payload=Depends(require_any_authenticated),
    service: BookingService = Depends(get_booking_service),
):
    return await service.delete_booking(booking_id)
