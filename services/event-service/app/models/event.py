from tortoise import fields
from tortoise.models import Model
import uuid


class Event(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    title = fields.CharField(max_length=255)
    description = fields.TextField()

    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()

    total_seats = fields.IntField()
    available_seats = fields.IntField()

    venue = fields.ForeignKeyField(
        "models.Venue",
        related_name="events",
        on_delete=fields.CASCADE
    )

    status = fields.CharField(
        max_length=20,
        default="ACTIVE"  # ACTIVE, CANCELLED, COMPLETED
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "events"