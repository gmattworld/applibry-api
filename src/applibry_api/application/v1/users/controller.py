from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette import status

from applibry_api.application.v1.apps.schema import AppSchema
from applibry_api.application.v1.apps.service import AppService, app_service
from applibry_api.application.v1.categories.schema import CategorySchema
from applibry_api.application.v1.categories.service import CategoryService, category_service
from applibry_api.application.v1.users.schema import (
    InviteUserSchema,
    UpdateUserProfileSchema,
    UpdateUserSchema,
    UserSchema,
)
from applibry_api.application.v1.users.service import UserService, user_service
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchemaExt,
    RouteResponseSchema,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: UserService = Depends(user_service),
):
    if lookup:
        data = await service.get_users_lookup()
        return RouteResponseSchemaExt[UserSchema](
            data=[UserSchema.model_validate(user) for user in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_users(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[UserSchema](
        data=[UserSchema.model_validate(user) for user in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/profile",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def profile(
    token: dict[str, str] = Depends(verify_token),
    service: UserService = Depends(user_service),
):
    data = await service.get_current_user(token)
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="User details"
    )


@router.get(
    "/libry",
    response_model=RouteResponseSchemaExt[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_libry(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    skip = (page - 1) * per_page
    data = await service.get_user_apps(
        decoded_token=token, limit=per_page, search=search
    )
    return RouteResponseSchemaExt[AppSchema](
        data=[AppSchema.model_validate(app) for app in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/preference",
    response_model=RouteResponseSchemaExt[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def get_user_preference(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    token: dict[str, str] = Depends(verify_token),
    service: CategoryService = Depends(category_service),
):
    skip = (page - 1) * per_page
    data = await service.get_user_categories(
        decoded_token=token, skip=skip, limit=per_page, search=search
    )
    return RouteResponseSchemaExt[CategorySchema](
        data=[CategorySchema.model_validate(app) for app in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def get_user(_id: UUID, service: UserService = Depends(user_service)):
    data = await service.get_user(_id)
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "/libry/{app_id}/add",
    response_model=RouteResponseSchema[str],
    status_code=status.HTTP_200_OK,
)
async def add_app_to_user_libry(
    app_id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: UserService = Depends(user_service),
):
    data = await service.add_to_user_libry(token, app_id)
    return RouteResponseSchema[str](
        data=data["message"], success=True, message=data["message"]
    )


@router.post(
    "/libry/{app_id}/remove",
    response_model=RouteResponseSchema[str],
    status_code=status.HTTP_200_OK,
)
async def remove_app_from_user_libry(
    app_id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: UserService = Depends(user_service),
):
    data = await service.remove_from_user_libry(token, app_id)
    return RouteResponseSchema[str](
        data=data["message"], success=True, message=data["message"]
    )


@router.post(
    "/preference/{category_id}/add",
    response_model=RouteResponseSchema[str],
    status_code=status.HTTP_200_OK,
)
async def add_app_to_user_preference(
    category_id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: UserService = Depends(user_service),
):
    data = await service.add_to_user_preference(token, category_id)
    return RouteResponseSchema[str](
        data=data["message"], success=True, message=data["message"]
    )


@router.post(
    "/preference/{category_id}/remove",
    response_model=RouteResponseSchema[str],
    status_code=status.HTTP_200_OK,
)
async def remove_app_from_user_preference(
    category_id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: UserService = Depends(user_service),
):
    data = await service.remove_from_user_preference(token, category_id)
    return RouteResponseSchema[str](
        data=data["message"], success=True, message=data["message"]
    )


@router.post(
    "/send-invite",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_201_CREATED,
)
async def invite_user(
    user: InviteUserSchema,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(user_service),
):
    data = await service.invite_user(user)

    # TODO: Revisit this
    # send_email(
    #     data.email,
    #     "Welcome to Applibry",
    #     """
    # <strong> You are invited to Applibry</strong>
    # <a href=https://Applibry.com>Click here</a>
    # """,
    #     background_tasks,
    # )
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="User created"
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def update_user(
    _id: UUID,
    request: UpdateUserSchema,
    service: UserService = Depends(user_service),
):
    data = await service.update_user(_id, request)
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="User Updated"
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def update_user_status(
    _id: UUID, service: UserService = Depends(user_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="User Updated"
    )


@router.put(
    "/{_id}/profile",
    response_model=RouteResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def update_user_profile(
    _id: UUID,
    request: UpdateUserProfileSchema,
    service: UserService = Depends(user_service),
):
    data = await service.update_user_profile(_id, request)
    return RouteResponseSchema[UserSchema](
        data=UserSchema.model_validate(data), success=True, message="Profile Updated"
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_user(_id: UUID, service: UserService = Depends(user_service)):
    deleted = await service.delete_user(_id)
    return RouteResponseSchema[None](
        data=None, success=deleted, message="User deleted"
    )
