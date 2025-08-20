from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from applibry_api.application.v1.roles.schema import (
    CreateRoleSchema,
    RoleSchema,
    RoleSchemaExt,
    UpdateRoleSchema,
)
from applibry_api.application.v1.roles.service import RoleService, role_service
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchemaExt,
    RouteResponseSchema,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[RoleSchema],
    status_code=status.HTTP_200_OK,
)
async def get_roles(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: RoleService = Depends(role_service),
):
    if lookup:
        data = await service.get_roles_lookup()
        return RouteResponseSchemaExt[RoleSchema](
            data=[RoleSchema.model_validate(role) for role in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_roles(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[RoleSchema](
        data=[RoleSchema.model_validate(role) for role in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[RoleSchemaExt],
    status_code=status.HTTP_200_OK,
)
async def get_role(_id: UUID, service: RoleService = Depends(role_service)):
    data = await service.get_role(_id)
    return RouteResponseSchema[RoleSchemaExt](
        data=RoleSchemaExt.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[RoleSchemaExt],
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role: CreateRoleSchema,
    token: dict[str, str] = Depends(verify_token),
    service: RoleService = Depends(role_service),
):
    data = await service.create_role(token, role)
    return RouteResponseSchema[RoleSchemaExt](
        data=RoleSchemaExt.model_validate(data), success=True, message="Role created"
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[RoleSchemaExt],
    status_code=status.HTTP_200_OK,
)
async def update_role(
    _id: UUID,
    request: UpdateRoleSchema,
    service: RoleService = Depends(role_service),
):
    data = await service.update_role(_id, request)
    return RouteResponseSchema[RoleSchemaExt](
        data=RoleSchemaExt.model_validate(data), success=True, message="Role Updated"
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[RoleSchema],
    status_code=status.HTTP_200_OK,
)
async def update_role_status(
    _id: UUID, service: RoleService = Depends(role_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[RoleSchema](
        data=RoleSchema.model_validate(data),
        success=True,
        message="Role Updated",
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_role(_id: UUID, service: RoleService = Depends(role_service)):
    deleted = await service.delete_role(_id)
    return RouteResponseSchema[None](data=None, success=deleted, message="Role deleted")
