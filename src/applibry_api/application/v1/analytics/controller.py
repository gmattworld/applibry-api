from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from applibry_api.infrastructure.persistence.database import get_db, verify_token
from applibry_api.domain.schemas.common_schema import RouteResponseSchema
from applibry_api.application.v1.analytics.schema import DashboardStatisticSchema, EntityStatisticSchema
from applibry_api.application.v1.analytics.service import AnalyticsService, analytics_service

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_db), Depends(verify_token)]
)

@router.get("/dashboard", response_model=RouteResponseSchema[DashboardStatisticSchema], status_code=status.HTTP_200_OK)
async def get_dashboard_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_dashboard_statistics()

    return RouteResponseSchema[DashboardStatisticSchema](
        data= DashboardStatisticSchema.model_validate(data),
        success=True,
        message="Dashboard statistics fetched successfully"
    )

@router.get("/category", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_category_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_category_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="Category statistics fetched successfully"
    )

@router.get("/app", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_app_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_app_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="App statistics fetched successfully"
    )

@router.get("/user", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_user_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_user_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="User statistics fetched successfully"
    ) 

@router.get("/role", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_role_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_role_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="Role statistics fetched successfully"
    )

@router.get("/permission", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_permission_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_permission_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="Permission statistics fetched successfully"
    )

@router.get("/platform", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_platform_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_platform_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="Platform statistics fetched successfully"
    )

@router.get("/tag", response_model=RouteResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
async def get_tag_statistics(service: AnalyticsService = Depends(analytics_service)):
    data = await service.get_tag_statistics()

    return RouteResponseSchema[EntityStatisticSchema](
        data= EntityStatisticSchema.model_validate(data),
        success=True,
        message="Tag statistics fetched successfully"
    )

