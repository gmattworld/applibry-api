import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseTagSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class CreateTagSchema(BaseTagSchema):
    pass


class UpdateTagSchema(BaseTagSchema):
    pass


class TagSchema(BaseTagSchema):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    last_updated_at: datetime
