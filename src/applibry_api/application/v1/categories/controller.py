from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from applibry_api.application.v1.categories.schema import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from applibry_api.application.v1.categories.service import CategoryService, category_service
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchema,
    RouteResponseSchemaExt,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def get_categories(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: CategoryService = Depends(category_service),
):
    if lookup:
        data = await service.get_categories_lookup()
        return RouteResponseSchemaExt[CategorySchema](
            data=[CategorySchema.model_validate(category) for category in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_categories(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[CategorySchema](
        data=[CategorySchema.model_validate(category) for category in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def get_category(
    _id: UUID, service: CategoryService = Depends(category_service)
):
    data = await service.get_category(_id)
    return RouteResponseSchema[CategorySchema](
        data=CategorySchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[CategorySchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CreateCategorySchema,
    token: dict[str, str] = Depends(verify_token),
    service: CategoryService = Depends(category_service),
):
    data = await service.create_category(token, category)
    return RouteResponseSchema[CategorySchema](
        data=CategorySchema.model_validate(data),
        success=True,
        message="Category created",
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def update_category(
    _id: UUID,
    request: UpdateCategorySchema,
    token: dict[str, str] = Depends(verify_token),
    service: CategoryService = Depends(category_service),
):
    data = await service.update_category(token, _id, request)
    return RouteResponseSchema[CategorySchema](
        data=CategorySchema.model_validate(data),
        success=True,
        message="Category Updated",
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[CategorySchema],
    status_code=status.HTTP_200_OK,
)
async def update_category_status(
    _id: UUID, service: CategoryService = Depends(category_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[CategorySchema](
        data=CategorySchema.model_validate(data),
        success=True,
        message="Category Updated",
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    _id: UUID, service: CategoryService = Depends(category_service)
):
    deleted = await service.delete_category(_id)
    return RouteResponseSchema[None](
        data=None, success=deleted, message="Category deleted"
    )
