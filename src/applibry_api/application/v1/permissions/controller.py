from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from applibry_api.application.v1.permissions.schema import (
    CreatePermissionSchema,
    PermissionSchema,
    UpdatePermissionSchema,
)
from applibry_api.application.v1.permissions.service import (
    PermissionService,
    permission_service,
)
from applibry_api.domain.schemas.common_schema import (
    RouteResponseSchemaExt,
    RouteResponseSchema,
)
from applibry_api.infrastructure.persistence.database import verify_token

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[Depends(verify_token)],
)


@router.get(
    "",
    response_model=RouteResponseSchemaExt[PermissionSchema],
    status_code=status.HTTP_200_OK,
)
async def get_permissions(
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
    lookup: bool = False,
    service: PermissionService = Depends(permission_service),
):
    if lookup:
        data = await service.get_permissions_lookup()
        return RouteResponseSchemaExt[PermissionSchema](
            data=[PermissionSchema.model_validate(permission) for permission in data],
            success=True,
            message="Success",
        )

    skip = (page - 1) * per_page
    data = await service.get_permissions(skip=skip, limit=per_page, search=search)
    return RouteResponseSchemaExt[PermissionSchema](
        data=[PermissionSchema.model_validate(permission) for permission in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )


@router.get(
    "/{_id}",
    response_model=RouteResponseSchema[PermissionSchema],
    status_code=status.HTTP_200_OK,
)
async def get_permission(
    _id: UUID, service: PermissionService = Depends(permission_service)
):
    data = await service.get_permission(_id)
    return RouteResponseSchema[PermissionSchema](
        data=PermissionSchema.model_validate(data), success=True, message="Success"
    )


@router.post(
    "",
    response_model=RouteResponseSchema[PermissionSchema],
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    permission: CreatePermissionSchema,
    token: dict[str, str] = Depends(verify_token),
    service: PermissionService = Depends(permission_service),
):
    data = await service.create_permission(token, permission)
    return RouteResponseSchema[PermissionSchema](
        data=PermissionSchema.model_validate(data),
        success=True,
        message="Permission created",
    )


@router.put(
    "/{_id}",
    response_model=RouteResponseSchema[PermissionSchema],
    status_code=status.HTTP_200_OK,
)
async def update_permission(
    _id: UUID,
    request: UpdatePermissionSchema,
    service: PermissionService = Depends(permission_service),
):
    data = await service.update_permission(_id, request)
    return RouteResponseSchema[PermissionSchema](
        data=PermissionSchema.model_validate(data),
        success=True,
        message="Permission Updated",
    )


@router.patch(
    "/{_id}/status",
    response_model=RouteResponseSchema[PermissionSchema],
    status_code=status.HTTP_200_OK,
)
async def update_permission_status(
    _id: UUID, service: PermissionService = Depends(permission_service)
):
    data = await service.change_status(_id)
    return RouteResponseSchema[PermissionSchema](
        data=PermissionSchema.model_validate(data),
        success=True,
        message="Permission Updated",
    )


@router.delete(
    "/{_id}",
    response_model=RouteResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def delete_permission(
    _id: UUID, service: PermissionService = Depends(permission_service)
):
    deleted = await service.delete_permission(_id)
    return RouteResponseSchema[None](
        data=None, success=deleted, message="Permission deleted"
    )
