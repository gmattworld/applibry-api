from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from applibry_api.application.v1.platforms.schema import (
    CreatePlatformSchema,
    PlatformSchema,
    UpdatePlatformSchema,
)
from applibry_api.application.v1.platforms.service import PlatformService, platform_service
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchemaExt,
    RouteResponseSchema,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/platforms",
    tags=["Platforms"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[PlatformSchema],
    status_code=status.HTTP_200_OK,
)
async def get_platforms(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: PlatformService = Depends(platform_service),
):
    if lookup:
        data = await service.get_platforms_lookup()
        return RouteResponseSchemaExt[PlatformSchema](
            data=[PlatformSchema.model_validate(platform) for platform in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_platforms(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[PlatformSchema](
        data=[PlatformSchema.model_validate(platform) for platform in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[PlatformSchema],
    status_code=status.HTTP_200_OK,
)
async def get_platform(
    _id: UUID, service: PlatformService = Depends(platform_service)
):
    data = await service.get_platform(_id)
    return RouteResponseSchema[PlatformSchema](
        data=PlatformSchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[PlatformSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_platform(
    platform: CreatePlatformSchema,
    token: dict[str, str] = Depends(verify_token),
    service: PlatformService = Depends(platform_service),
):
    data = await service.create_platform(token, platform)
    return RouteResponseSchema[PlatformSchema](
        data=PlatformSchema.model_validate(data),
        success=True,
        message="Platform created",
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[PlatformSchema],
    status_code=status.HTTP_200_OK,
)
async def update_platform(
    _id: UUID,
    request: UpdatePlatformSchema,
    token: dict[str, str] = Depends(verify_token),
    service: PlatformService = Depends(platform_service),
):
    data = await service.update_platform(token, _id, request)
    return RouteResponseSchema[PlatformSchema](
        data=PlatformSchema.model_validate(data),
        success=True,
        message="Platform Updated",
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[PlatformSchema],
    status_code=status.HTTP_200_OK,
)
async def update_platform_status(
    _id: UUID, service: PlatformService = Depends(platform_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[PlatformSchema](
        data=PlatformSchema.model_validate(data),
        success=True,
        message="Platform Updated",
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_platform(
    _id: UUID, service: PlatformService = Depends(platform_service)
):
    deleted = await service.delete_platform(_id)
    return RouteResponseSchema[None](
        data=None, success=deleted, message="Platform deleted"
    )
