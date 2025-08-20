# from uuid import UUID

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from starlette import status

# from applibry_api.infrastructure.persistence.database import get_db, verify_token
# from applibry_api.schemas.common_schema import AppResponseSchema
# from applibry_api.schemas.statistics_schema import DashboardStatisticSchema, EntityStatisticSchema
# from applibry_api.services import statistics_service

# router = APIRouter(
#     prefix="/api/statistics",
#     tags=["Statistics"],
#     dependencies=[Depends(get_db), Depends(verify_token)]
# )

# @router.get("/dashboard", response_model=AppResponseSchema[DashboardStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_dashboard_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_dashboard_statistics(db, _token)

#     return AppResponseSchema[DashboardStatisticSchema](
#         data= DashboardStatisticSchema.model_validate(data),
#         success=True,
#         message="Dashboard statistics fetched successfully"
#     )

# @router.get("/category", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_category_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_category_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="Category statistics fetched successfully"
#     )

# @router.get("/app", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_app_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_app_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="App statistics fetched successfully"
#     )

# @router.get("/user", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_user_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_user_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="User statistics fetched successfully"
#     ) 

# @router.get("/role", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_role_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_role_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="Role statistics fetched successfully"
#     )

# @router.get("/permission", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_permission_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_permission_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="Permission statistics fetched successfully"
#     )

# @router.get("/platform", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_platform_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_platform_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="Platform statistics fetched successfully"
#     )

# @router.get("/tag", response_model=AppResponseSchema[EntityStatisticSchema], status_code=status.HTTP_200_OK)
# async def get_tag_statistics(_token:dict[str, str]=Depends(verify_token), db: Session = Depends(get_db)):
#     data = statistics_service.get_tag_statistics(db, _token)

#     return AppResponseSchema[EntityStatisticSchema](
#         data= EntityStatisticSchema.model_validate(data),
#         success=True,
#         message="Tag statistics fetched successfully"
#     )


