from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status

from applibry_api.application.v1.apps.schema import (
    AppSchema,
    CreateAppSchema,
    UpdateAppSchema,
)
from applibry_api.application.v1.apps.service import AppService, app_service
from applibry_api.domain.schemas.common_schema import RouteResponseSchema, RouteResponseSchemaExt
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/apps",
    tags=["Apps"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def get_apps(
    search: Optional[str] = None,
    personalised: bool = True,
    category: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = 20,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    data = await service.get_apps(
        decoded_token=token,
        limit=limit,
        cursor=cursor,
        personalised=personalised,
        search=search,
        category=category,
    )
    return RouteResponseSchemaExt[AppSchema](
        data=[AppSchema.model_validate(app) for app in data["data"]],
        next_cursor=data["next_cursor"],
        success=True,
        message="Success",
    )


@router.get(
    "/trending",
    response_model=RouteResponseSchemaExt[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def get_trending_apps(
    page_size: int = Query(1, gt=0),
    category: Optional[str] = None,
    cursor: Optional[str] = None,
    service: AppService = Depends(app_service),
):
    data = await service.get_trending_apps(limit=page_size, category=category, cursor=cursor)
    return RouteResponseSchemaExt[AppSchema](
        data=[AppSchema.model_validate(app) for app in data["data"]],
        next_cursor=data["next_cursor"],
        success=True,
        message="Success",
    )


@router.get(
    "/{slug}",
    response_model=RouteResponseSchema[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def get_app(
    slug: str,
    service: AppService = Depends(app_service),
):
    data = await service.get_app(slug)
    return RouteResponseSchema[AppSchema](
        data=AppSchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[AppSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_app(
    app: CreateAppSchema,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    data = await service.create_app(token, app)
    return RouteResponseSchema[AppSchema](
        data=AppSchema.model_validate(data), success=True, message="App created"
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def update_app(
    _id: UUID,
    request: UpdateAppSchema,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    data = await service.update_app(token, _id, request)
    return RouteResponseSchema[AppSchema](
        data=AppSchema.model_validate(data), success=True, message="App updated"
    )


@router.put(
    "/{_id}/publish",
    response_model=RouteResponseSchema[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def publish_app(
    _id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    data = await service.publish_app(token, _id)
    return RouteResponseSchema[AppSchema](
        data=AppSchema.model_validate(data), success=True, message="App published"
    )


@router.patch(
    "/{_id}/revert",
    response_model=RouteResponseSchema[AppSchema],
    status_code=status.HTTP_200_OK,
)
async def revert_app_to_draft(
    _id: UUID,
    token: dict[str, str] = Depends(verify_token),
    service: AppService = Depends(app_service),
):
    data = await service.revert_to_draft(token, _id)
    return RouteResponseSchema[AppSchema](
        data=AppSchema.model_validate(data),
        success=True,
        message="App reverted to draft",
    )
