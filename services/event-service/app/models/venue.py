from tortoise import fields
from tortoise.models import Model
import uuid


class Venue(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    location = fields.CharField(max_length=255)
    capacity = fields.IntField()

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "venues"

    def __str__(self):
        return self.name