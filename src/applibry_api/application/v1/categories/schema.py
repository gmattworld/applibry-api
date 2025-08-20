import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class CreateCategorySchema(BaseCategorySchema):
    pass


class UpdateCategorySchema(BaseCategorySchema):
    pass


class CategorySchema(BaseCategorySchema):
    id: uuid.UUID
    is_active: bool
    icon: Optional[str]
    app_count: Optional[int]
    subscribers: Optional[int]
    created_at: datetime
    last_updated_at: datetime
