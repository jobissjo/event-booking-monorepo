from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.deps import require_organizer_or_admin, require_any_authenticated
from app.schemas.event import (
    VenueCreate, VenueUpdate, VenueResponse,
    EventCreate, EventUpdate, EventResponse,
)
from app.services.event_service import VenueService, EventService

router = APIRouter()

# ─────────────────────── Venue dependency ───────────────────────

def get_venue_service() -> VenueService:
    return VenueService()


def get_event_service() -> EventService:
    return EventService()


# ═══════════════════════════ VENUE ROUTES ═══════════════════════════

@router.post(
    "/venues",
    response_model=VenueResponse,
    status_code=201,
    summary="Create a venue (organizer / admin only)",
)
async def create_venue(
    data: VenueCreate,
    _payload=Depends(require_organizer_or_admin),  # role guard
    service: VenueService = Depends(get_venue_service),
):
    """
    Create a new venue.
    **Requires role:** `organizer` or `admin`
    """
    return await service.create_venue(data)


@router.get(
    "/venues",
    response_model=List[VenueResponse],
    summary="List all venues",
)
async def list_venues(
    _payload=Depends(require_any_authenticated),
    service: VenueService = Depends(get_venue_service),
):
    return await service.list_venues()


@router.get(
    "/venues/{venue_id}",
    response_model=VenueResponse,
    summary="Get venue by ID",
)
async def get_venue(
    venue_id: UUID,
    _payload=Depends(require_any_authenticated),
    service: VenueService = Depends(get_venue_service),
):
    return await service.get_venue(venue_id)


@router.put(
    "/venues/{venue_id}",
    response_model=VenueResponse,
    summary="Update a venue (organizer / admin only)",
)
async def update_venue(
    venue_id: UUID,
    data: VenueUpdate,
    _payload=Depends(require_organizer_or_admin),
    service: VenueService = Depends(get_venue_service),
):
    return await service.update_venue(venue_id, data)


@router.delete(
    "/venues/{venue_id}",
    summary="Delete a venue (organizer / admin only)",
)
async def delete_venue(
    venue_id: UUID,
    _payload=Depends(require_organizer_or_admin),
    service: VenueService = Depends(get_venue_service),
):
    return await service.delete_venue(venue_id)


# ═══════════════════════════ EVENT ROUTES ═══════════════════════════

@router.post(
    "/events",
    response_model=EventResponse,
    status_code=201,
    summary="Create an event with its venue (organizer / admin only)",
)
async def create_event(
    data: EventCreate,
    _payload=Depends(require_organizer_or_admin),  # role guard
    service: EventService = Depends(get_event_service),
):
    """
    Create a new event linked to an existing venue.

    - **venue_id**: must be an existing venue UUID
    - **total_seats**: must not exceed the venue's capacity
    - Only **organizer** or **admin** roles can call this endpoint.
    """
    return await service.create_event(data)


@router.get(
    "/events",
    response_model=List[EventResponse],
    summary="List all events",
)
async def list_events(
    _payload=Depends(require_any_authenticated),
    service: EventService = Depends(get_event_service),
):
    return await service.list_events()


@router.get(
    "/events/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID",
)
async def get_event(
    event_id: UUID,
    _payload=Depends(require_any_authenticated),
    service: EventService = Depends(get_event_service),
):
    return await service.get_event(event_id)


@router.put(
    "/events/{event_id}",
    response_model=EventResponse,
    summary="Update an event (organizer / admin only)",
)
async def update_event(
    event_id: UUID,
    data: EventUpdate,
    _payload=Depends(require_organizer_or_admin),
    service: EventService = Depends(get_event_service),
):
    return await service.update_event(event_id, data)


@router.delete(
    "/events/{event_id}",
    summary="Delete an event (organizer / admin only)",
)
async def delete_event(
    event_id: UUID,
    _payload=Depends(require_organizer_or_admin),
    service: EventService = Depends(get_event_service),
):
    return await service.delete_event(event_id)
