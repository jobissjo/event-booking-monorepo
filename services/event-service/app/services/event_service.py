from uuid import UUID
from typing import List

from app.models.venue import Venue
from app.models.event import Event
from app.schemas.event import VenueCreate, VenueUpdate, EventCreate, EventUpdate
from app.core.exceptions import AppException


# ═══════════════════════ Venue Service ════════════════════════

class VenueService:

    async def create_venue(self, data: VenueCreate) -> Venue:
        venue = await Venue.create(
            name=data.name,
            location=data.location,
            capacity=data.capacity,
        )
        return venue

    async def get_venue(self, venue_id: UUID) -> Venue:
        venue = await Venue.get_or_none(id=venue_id)
        if not venue:
            raise AppException(status_code=404, detail="Venue not found")
        return venue

    async def list_venues(self) -> List[Venue]:
        return await Venue.all()

    async def update_venue(self, venue_id: UUID, data: VenueUpdate) -> Venue:
        venue = await self.get_venue(venue_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise AppException(status_code=400, detail="No fields provided for update")
        await venue.update_from_dict(update_data).save()
        await venue.refresh_from_db()
        return venue

    async def delete_venue(self, venue_id: UUID) -> dict:
        venue = await self.get_venue(venue_id)
        await venue.delete()
        return {"detail": "Venue deleted successfully"}


# ═══════════════════════ Event Service ════════════════════════

class EventService:

    async def create_event(self, data: EventCreate) -> Event:
        # Validate venue exists
        venue = await Venue.get_or_none(id=data.venue_id)
        if not venue:
            raise AppException(status_code=404, detail="Venue not found")

        # Ensure event seats do not exceed venue capacity
        if data.total_seats > venue.capacity:
            raise AppException(
                status_code=400,
                detail=f"total_seats ({data.total_seats}) exceeds venue capacity ({venue.capacity})"
            )

        event = await Event.create(
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            total_seats=data.total_seats,
            available_seats=data.total_seats,  # starts fully available
            venue=venue,
        )
        await event.fetch_related("venue")
        return event

    async def get_event(self, event_id: UUID) -> Event:
        event = await Event.get_or_none(id=event_id).prefetch_related("venue")
        if not event:
            raise AppException(status_code=404, detail="Event not found")
        return event

    async def list_events(self) -> List[Event]:
        return await Event.all().prefetch_related("venue")

    async def update_event(self, event_id: UUID, data: EventUpdate) -> Event:
        event = await self.get_event(event_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise AppException(status_code=400, detail="No fields provided for update")

        # If venue_id is being changed, validate the new venue
        if "venue_id" in update_data:
            venue = await Venue.get_or_none(id=update_data.pop("venue_id"))
            if not venue:
                raise AppException(status_code=404, detail="Venue not found")
            update_data["venue"] = venue

        # Validate total_seats against venue capacity
        if "total_seats" in update_data:
            venue = await event.venue
            cap = update_data["total_seats"]
            if cap > venue.capacity:
                raise AppException(
                    status_code=400,
                    detail=f"total_seats ({cap}) exceeds venue capacity ({venue.capacity})"
                )

        # Validate status value if provided
        if "status" in update_data:
            allowed = {"ACTIVE", "CANCELLED", "COMPLETED"}
            if update_data["status"] not in allowed:
                raise AppException(
                    status_code=400,
                    detail=f"Invalid status. Allowed values: {allowed}"
                )

        await event.update_from_dict(update_data).save()
        await event.fetch_related("venue")
        return event

    async def delete_event(self, event_id: UUID) -> dict:
        event = await self.get_event(event_id)
        await event.delete()
        return {"detail": "Event deleted successfully"}
