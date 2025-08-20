import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from applibry_api.application.v1.categories.schema import CategorySchema
from applibry_api.application.v1.platforms.schema import PlatformSchema
from applibry_api.application.v1.tags.schema import TagSchema
from applibry_api.domain.enums.app_status import AppStatus
from applibry_api.domain.enums.pricing_model import PricingModel


class BaseAppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    brief: str
    price: float
    website: str
    meta_title: str
    meta_keywords: str
    meta_description: str
    icon: Optional[str]
    banner: Optional[str]
    status: AppStatus
    pricing_model: PricingModel
    category_id: uuid.UUID


class CreateAppSchema(BaseAppSchema):
    tags: list[uuid.UUID]
    platforms: list[uuid.UUID]


class UpdateAppSchema(BaseAppSchema):
    tags: list[uuid.UUID]
    platforms: list[uuid.UUID]


class UpdateAppMetaSchema(BaseAppSchema):
    banner: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    tags: Optional[list[uuid.UUID]] = None
    publish: Optional[bool] = False


class AppSchema(BaseAppSchema):
    id: uuid.UUID
    subscribers: Optional[int]
    ratings: Optional[int]
    reviews: Optional[int]
    shares: Optional[int]
    rank: Optional[int]
    slug: Optional[str]
    category: Optional[CategorySchema]
    tags: Optional[list[TagSchema]]
    platforms: Optional[list[PlatformSchema]]
    published_at: Optional[datetime]
    created_at: datetime
    last_updated_at: datetime
