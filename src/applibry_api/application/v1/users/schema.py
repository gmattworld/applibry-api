import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseUserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name: str
    last_name: str
    email: str


class InviteUserSchema(BaseUserSchema):
    role_id: uuid.UUID


class CreateUserSchema(BaseUserSchema):
    role_id: uuid.UUID
    password: str


class UpdateUserSchema(BaseUserSchema):
    role_id: uuid.UUID


class UserSchema(BaseUserSchema):
    id: uuid.UUID
    is_active: Optional[bool]
    username: Optional[str]
    email_confirmed: Optional[bool]
    is_admin: Optional[bool]
    receive_newsletter: Optional[bool]
    country: Optional[str]
    profession: Optional[str]
    phone_number: Optional[str]
    phone_number_confirmed: Optional[bool]
    two_factor_enabled: Optional[bool]
    lockout_end: Optional[str]
    lockout_enabled: Optional[bool]
    access_failed_count: Optional[int]
    role_id: Optional[uuid.UUID]
    account_type: Optional[str]
    last_subscription_date: Optional[datetime]
    next_subscription_date: Optional[datetime]
    is_verified: Optional[bool]
    is_verified_at: Optional[datetime]
    is_preference_configured: Optional[bool]
    deleted_at: Optional[datetime]
    is_deleted: Optional[bool]
    deleted_by_id: Optional[uuid.UUID]
    created_by_id: Optional[uuid.UUID]
    created_at: Optional[datetime]
    last_updated_by_id: Optional[uuid.UUID]
    last_updated_at: Optional[datetime]


# class UserResponseSchema(BaseModel):
#     data: Optional[UserSchema]
#     success: bool = True
#     message: str = ""
#     status_code: int = 200

class UpdateUserProfileSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    profession: Optional[str]
    country: Optional[str]

# class UserResponseSchemaExt(BaseModel):
#     data: Optional[list[UserSchema]]
#     current_page: int = 0
#     page_size: int = 0
#     total: int = 0
#     success: bool = True
#     message: str = ""
#     status_code: int = 200
