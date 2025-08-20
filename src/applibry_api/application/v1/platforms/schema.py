import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BasePlatformSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class CreatePlatformSchema(BasePlatformSchema):
    pass


class UpdatePlatformSchema(BasePlatformSchema):
    pass


class PlatformSchema(BasePlatformSchema):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    last_updated_at: datetime
