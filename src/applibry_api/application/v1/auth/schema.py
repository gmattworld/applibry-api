import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from applibry_api.domain.enums.account_type import AccountType
from applibry_api.application.v1.users.schema import UserSchema


class BaseAuthSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str


class LoginSchema(BaseAuthSchema):
    password: str


class RegisterSchema(BaseAuthSchema):
    first_name: str
    last_name: str
    password: str
    account_type: Optional[AccountType]


class VerifyPasswordResetSchema(BaseAuthSchema):
    otp: str


class ResetPasswordSchema(BaseAuthSchema):
    new_password: str


class ChangePasswordSchema(BaseAuthSchema):
    current_password: str
    new_password: str


class VerifySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_key: str
    code: str


class VerifyPreferenceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str

class TokenRefreshRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    refresh_token: str

class RegenerateVerificationCodeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    public_key: str


class AuthSchema(BaseAuthSchema):
    id: Optional[uuid.UUID]
    last_name: Optional[str]
    first_name: Optional[str]
    public_key: Optional[str]


class AuthSchemaExt(UserSchema):
    pass


class TokenSchema(BaseModel):
    token: str
    type: str
    expires_in: datetime


class AuthResponseSchema(BaseModel):
    data: Optional[AuthSchema] = None
    success: bool = True
    message: str = ""
    status_code: int = 200


class AuthResponseSchemaExt(BaseModel):
    data: Optional[AuthSchemaExt] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[datetime] = None
    success: bool = True
    message: str = ""
    status_code: int = 200
