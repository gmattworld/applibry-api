import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from applibry_api.domain.enums.modules import Modules


class BasePermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    module_id: uuid.UUID


class CreatePermissionSchema(BasePermissionSchema):
    pass


class UpdatePermissionSchema(BasePermissionSchema):
    pass


class PermissionSchema(BasePermissionSchema):
    id: uuid.UUID
    is_active: bool
    code: str
    module: Modules
    created_at: datetime
    last_updated_at: datetime
