import datetime
from datetime import timedelta
from typing import Annotated

from decouple import config
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from applibry_api.domain.entities.user import User
from applibry_api.domain.utilities import token_service
from applibry_api.infrastructure.persistence.database import get_db, oauth2_scheme, verify_token
from applibry_api.domain.exceptions.base_exception import AppBadRequestException
from applibry_api.application.v1.auth.schema import (
    AuthResponseSchema,
    AuthResponseSchemaExt,
    AuthSchema,
    AuthSchemaExt,
    BaseAuthSchema,
    ChangePasswordSchema,
    RegenerateVerificationCodeSchema,
    RegisterSchema,
    ResetPasswordSchema,
    TokenRefreshRequest,
    VerifyPasswordResetSchema,
    VerifyPreferenceSchema,
    VerifySchema,
)
from applibry_api.application.v1.auth.service import AuthService, auth_service
from applibry_api.application.v1.users.service import UserService, user_service
from applibry_api.domain.utilities.email_template_manager import (
    get_password_reset_template,
    get_registration_template,
)
from applibry_api.domain.utilities.tokenizer import generate_secure_number

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[Depends(get_db)]
)


@router.post("/register", response_model=AuthResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(auth_service),
):
    code = str(generate_secure_number(8))
    data = await service.register(request, code)
    registration_email_content = get_registration_template(data.first_name, code)
    # TODO: Revisit this
    # send_email(
    #     data.email, "Welcome to Applibry", registration_email_content, background_tasks
    # )
    response = AuthSchema.model_validate(data)
    return AuthResponseSchema(data=response, success=True, message="User created")


@router.post("/send-email-verification", response_model=AuthResponseSchema, status_code=status.HTTP_201_CREATED)
async def send_email_verification(
    background_tasks: BackgroundTasks,
):
    code = str(generate_secure_number(8))
    registration_email_content = get_registration_template("John Doe", code)
    # TODO: Revisit this
    # send_email(
    #     "gmattworld@gmail.com", "Welcome to Applibry", registration_email_content, background_tasks
    # )
    return AuthResponseSchema(success=True, message="Email verification sent")


@router.post("/resend-email-verification", response_model=AuthResponseSchema, status_code=status.HTTP_201_CREATED)
async def resend_email_verification(
    request: RegenerateVerificationCodeSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(auth_service),
):
    code = str(generate_secure_number(8))
    data = await service.regenerate_email_verification_code(
        code, request.public_key
    )
    registration_email_content = get_registration_template(data.first_name, code)
    # TODO: Revisit this
    # send_email(
    #     data.email, "Welcome to Applibry", registration_email_content, background_tasks
    # )
    response = AuthSchema.model_validate(data)
    return AuthResponseSchema(
        data=response, success=True, message="Verification code sent"
    )


@router.post("/initiate-password-reset", response_model=AuthResponseSchema, status_code=status.HTTP_200_OK)
async def initiate_password_reset(
    request: BaseAuthSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(auth_service),
):
    code = str(generate_secure_number(8))
    data = await service.initiate_password_reset(request.email, code)
    password_reset_email_content = get_password_reset_template(data.first_name, code)
    # TODO: Revisit this
    # send_email(
    #     data.email,
    #     "Applibry Reset Password Verification",
    #     password_reset_email_content,
    #     background_tasks,
    # )
    response = AuthSchema.model_validate(data)

    return AuthResponseSchema(
        data=response,
        success=True,
        message="We have sent a One-Time Password (OTP) to your email address",
    )


@router.post("/verify-password-reset", response_model=AuthResponseSchema, status_code=status.HTTP_200_OK)
async def verify_password_reset_code(
    request: VerifyPasswordResetSchema, service: AuthService = Depends(auth_service)
):
    data = await service.verify_password_reset(request.otp, request.email)
    response = AuthSchema.model_validate(data)
    return AuthResponseSchema(
        data=response, success=True, message="Password reset verified"
    )


@router.post("/reset-password", response_model=AuthResponseSchemaExt, status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordSchema,
    token: dict = Depends(verify_token),
    auth_service_instance: AuthService = Depends(auth_service),
    user_service_instance: UserService = Depends(user_service),
):
    profile = await user_service_instance.get_current_user(token)
    if profile.email != request.email:
        raise AppBadRequestException("Email address is incorrect")

    data = await auth_service_instance.reset_password(
        request.new_password, request.email
    )
    return get_auth_response(data)


@router.post("/change-password", response_model=AuthResponseSchemaExt, status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordSchema,
    token: dict = Depends(verify_token),
    auth_service_instance: AuthService = Depends(auth_service),
    user_service_instance: UserService = Depends(user_service),
):
    profile = await user_service_instance.get_current_user(token)
    if profile.email != request.email:
        raise AppBadRequestException("Could not validate user")

    data = await auth_service_instance.change_password(
        request.current_password, request.new_password, request.email
    )
    return get_auth_response(data)


@router.post("/verify", response_model=AuthResponseSchemaExt, status_code=status.HTTP_201_CREATED)
async def verify(
    request: VerifySchema, service: AuthService = Depends(auth_service)
):
    data = await service.verify(request.code, request.public_key)
    return get_auth_response(data)


@router.put("/verify_preference_config", response_model=AuthResponseSchemaExt, status_code=status.HTTP_200_OK)
async def verify_preference_config(
    request: VerifyPreferenceSchema,
    token: dict = Depends(verify_token),
    auth_service_instance: AuthService = Depends(auth_service),
    user_service_instance: UserService = Depends(user_service),
):
    profile = await user_service_instance.get_current_user(token)
    if profile.email != request.email:
        raise AppBadRequestException("Could not validate user")

    data = await auth_service_instance.verify_preference_config(request.email)
    return get_auth_response(data)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(auth_service),
):
    data = await service.login(form_data.username, form_data.password)

    if not data.is_verified:
        response = AuthSchema.model_validate(data)
        return AuthResponseSchema(
            data=response,
            success=True,
            message="Account not verified",
        )

    return get_auth_response(data)


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    req: TokenRefreshRequest, service: AuthService = Depends(auth_service)
):
    data = await service.refresh(req.refresh_token)

    if not data.is_verified:
        response = AuthSchema.model_validate(data)
        return AuthResponseSchema(
            data=response,
            success=True,
            message="Account not verified",
        )

    return get_auth_response(data)


def get_auth_response(data: User):
    access_token = token_service.create_access_token(data)
    refresh_token = token_service.create_refresh_token(data)
    access_token_lifetime = config("ACCESS_TOKEN_EXPIRES_IN_MINS", cast=int)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=access_token_lifetime
    )

    response = AuthSchemaExt.model_validate(data)
    return AuthResponseSchemaExt(
        data=response,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=expiration_time,
        success=True,
        message="Login successful",
    ) 