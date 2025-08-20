import uuid
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel, ConfigDict
from starlette import status

T = TypeVar('T')

@dataclass
class ServiceResponseSchema(Generic[T]):
    status: bool = True
    message: str = ""
    data: Optional[T] = None


class SeederResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    response: Optional[str]


class LookupSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[uuid.UUID]
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    banner: Optional[str] = None


class RouteResponseSchema(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    data: Optional[T] = None
    success: bool = True
    message: str = ""
    status_code: int = 200

class RouteResponseSchemaExt(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    data: Optional[list[T]] = None
    next_cursor: Optional[str] = None
    success: bool = True
    message: str = ""
    status_code: int = 200


class RouteErrorResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    message: str
    success: bool = False
    status_code: int = status.HTTP_400_BAD_REQUEST


# class AppResponseSchema(BaseModel, Generic[T]):
#     data: Optional[T] = None
#     success: bool = True
#     message: str = ""
#     status_code: int = 200


# class AppResponseSchemaExt(BaseModel, Generic[T]):
#     model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
#     data: Optional[list[T]] = None
#     current_page: int = 0
#     page_size: int = 0
#     total: int = 0
#     success: bool = True
#     message: str = ""
#     status_code: int = 200
