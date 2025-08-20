import uuid
from datetime import datetime
from typing import Optional, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from applibry_api.domain.schemas.common_schema import LookupSchema

T = TypeVar('T')

class BaseAppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class AppLoginSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client_id: str
    client_secret: str


class AppAuthResponseSchema(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[datetime] = None
    success: bool = True
    message: str = ""
    status_code: int = 200


class AppResponseSchema(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    data: T | None
    success: bool
    message: str
    status_code: int = 200


class AppResponseSchemaExt(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    data: Optional[list[T]] = None
    current_page: int = 0
    page_size: int = 0
    total: int = 0
    success: bool = True
    message: str = ""
    status_code: int = 200


class AppCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: Optional[str] = None
    description: Optional[str] = None
    is_nav: Optional[bool] = False
    is_featured: Optional[bool] = False


class AppQuoteSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    content: str
    background: Optional[str]
    status: str
    tags: Optional[list[LookupSchema]]
    author: Optional[LookupSchema]


class AppArticleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    body: str
    brief: Optional[str] = None
    likes: Optional[int] = None
    slug: Optional[str] = None
    banner: Optional[str] = None
    published_at: datetime | None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    category: Optional[LookupSchema] = None
    author: Optional[LookupSchema] = None
    tags: Optional[list[LookupSchema]] = None
