from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityResponse(BaseModel):
    id: UUID
    user_id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
