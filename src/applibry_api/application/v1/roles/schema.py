import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from applibry_api.application.v1.permissions.schema import PermissionSchema


class BaseRoleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    is_system_role: bool


class CreateRoleSchema(BaseRoleSchema):
    permissions: list[uuid.UUID]


class UpdateRoleSchema(BaseRoleSchema):
    permissions: list[uuid.UUID]


class RoleSchema(BaseRoleSchema):
    id: uuid.UUID
    is_active: bool
    code: str
    created_at: datetime
    last_updated_at: datetime


class RoleSchemaExt(RoleSchema):
    permissions: list[PermissionSchema]
