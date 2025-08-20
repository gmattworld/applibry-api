from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from applibry_api.application.v1.apps.schema import AppSchema
from applibry_api.application.v1.apps.service import AppService, app_service
from applibry_api.application.v1.categories.schema import CategorySchema
from applibry_api.application.v1.categories.service import CategoryService, category_service
from applibry_api.domain.enums.lookup_type import LookupType
from applibry_api.domain.schemas.common_schema import LookupSchema, RouteResponseSchemaExt
from applibry_api.infrastructure.persistence.database import get_db, verify_token
from applibry_api.infrastructure.providers.nattypad.schemas.app_schema import AppResponseSchemaExt


router = APIRouter(
    prefix="/public",
    tags=["public"],
    dependencies=[Depends(get_db)]
)


@router.get("/apps", response_model=RouteResponseSchemaExt[AppSchema], status_code=status.HTTP_200_OK)
async def get_apps(category: Optional[str] = None, page: int = 1, per_page: int = 20, db: Session = Depends(get_db), _app_service: AppService = Depends(app_service)):
    if page <= 0:
        page = 1

    if per_page <= 0:
        per_page = 20

    skip = (page - 1) * per_page
    limit = per_page
    data = await _app_service.get_trending_apps(limit=limit, category=category)
    return RouteResponseSchemaExt[AppSchema](
        data=[AppSchema.model_validate(app) for app in data["data"]],
        next_cursor=data["next_cursor"],
        success=True,
        message="Success",
    )

@router.get("/categories", response_model=RouteResponseSchemaExt[CategorySchema], status_code=status.HTTP_200_OK)
async def get_categories(search: str = None, page: int = 1, per_page: int = 20, db: Session = Depends(get_db), _category_service: CategoryService = Depends(category_service)):
    if page <= 0:
        page = 1

    if per_page <= 0:
        per_page = 20

    skip = (page - 1) * per_page
    limit = per_page
    data = await _category_service.get_categories(skip=skip, limit=limit, search=search)
    return RouteResponseSchemaExt[CategorySchema](
        data=[CategorySchema.model_validate(category) for category in data["data"]],
        success=True,
        current_page=page,
        page_size=per_page,
        total=data["total"],
        message="Success",
    )

# @router.get("", response_model=AppResponseSchemaExt[LookupSchema], status_code=status.HTTP_200_OK)
# async def get_lookups(_type: LookupType, _token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = lookup_service.get_lookups(db, _type)
#     return AppResponseSchemaExt[LookupSchema](
#         data=[LookupSchema.model_validate(lookup) for lookup in data],
#         success=True,
#         current_page=0,
#         page_size=0,
#         total=0,
#         message="Success"
#     )
