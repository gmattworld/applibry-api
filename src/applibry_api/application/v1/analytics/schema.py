import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from applibry_api.application.v1.permissions.schema import PermissionSchema


class BaseStatisticSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    is_system_role: bool


class DashboardStatisticSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    MylibryAppCount: int
    PreferenceCount: int
    InteractionCount: int
    SubmissionCount: int

class EntityStatisticSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ActiveCount: int
    InactiveCount: int
    TotalCount: int


class CategoryStatisticSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    is_system_role: bool

class StatisticSchema(BaseStatisticSchema):
    id: uuid.UUID
    is_active: bool
    code: str
    created_at: datetime
    last_updated_at: datetime


class StatisticSchemaExt(StatisticSchema):
    permissions: list[PermissionSchema]


class StatisticResponseSchema(BaseModel):
    data: StatisticSchemaExt | None
    success: bool = True
    message: str = ""
    status_code: int = 200


class StatisticResponseSchemaExt(BaseModel):
    data: list[StatisticSchema] | None
    current_page: int = 0
    page_size: int = 0
    total: int = 0
    success: bool = True
    message: str = ""
    status_code: int = 200
