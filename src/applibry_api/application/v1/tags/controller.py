from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from applibry_api.application.v1.tags.schema import CreateTagSchema, TagSchema, UpdateTagSchema
from applibry_api.application.v1.tags.service import TagService, tag_service
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchemaExt,
    RouteResponseSchema,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[TagSchema],
    status_code=status.HTTP_200_OK,
)
async def get_tags(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: TagService = Depends(tag_service),
):
    if lookup:
        data = await service.get_tags_lookup()
        return RouteResponseSchemaExt[TagSchema](
            data=[TagSchema.model_validate(tag) for tag in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_tags(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[TagSchema](
        data=[TagSchema.model_validate(tag) for tag in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[TagSchema],
    status_code=status.HTTP_200_OK,
)
async def get_tag(_id: UUID, service: TagService = Depends(tag_service)):
    data = await service.get_tag(_id)
    return RouteResponseSchema[TagSchema](
        data=TagSchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[TagSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag: CreateTagSchema,
    token: dict[str, str] = Depends(verify_token),
    service: TagService = Depends(tag_service),
):
    data = await service.create_tag(token, tag)
    return RouteResponseSchema[TagSchema](
        data=TagSchema.model_validate(data), success=True, message="Tag created"
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[TagSchema],
    status_code=status.HTTP_200_OK,
)
async def update_tag(
    _id: UUID,
    request: UpdateTagSchema,
    service: TagService = Depends(tag_service),
):
    data = await service.update_tag(_id, request)
    return RouteResponseSchema[TagSchema](
        data=TagSchema.model_validate(data), success=True, message="Tag Updated"
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[TagSchema],
    status_code=status.HTTP_200_OK,
)
async def update_tag_status(
    _id: UUID, service: TagService = Depends(tag_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[TagSchema](
        data=TagSchema.model_validate(data),
        success=True,
        message="Tag Updated",
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_tag(_id: UUID, service: TagService = Depends(tag_service)):
    deleted = await service.delete_tag(_id)
    return RouteResponseSchema[None](data=None, success=deleted, message="Tag deleted")
