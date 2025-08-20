import asyncio
import sys

from decouple import config
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from applibry_api.application.v1 import apps, auth, categories, permissions, platforms, public, roles, tags, users
from applibry_api.application.v1 import integrations
from applibry_api.application.v1 import analytics
from applibry_api.application.v1.analytics import controller
from applibry_api.infrastructure.persistence.database import get_db
from applibry_api.domain.exceptions.base_exception import AppBaseException
from applibry_api.domain.schemas.common_schema import RouteErrorResponseSchema

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

IS_PROD = config("IS_PROD", cast=bool, default=True)
app = FastAPI(
    title="Applibry API",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
    dependencies=[Depends(get_db)]
)

@app.exception_handler(AppBaseException)
async def base_exception_handler(request: Request, exc: AppBaseException):
    return JSONResponse(
        status_code=exc.status_code,
        content=RouteErrorResponseSchema(
            message=exc.detail,
            status_code=exc.status_code
        ).model_dump()
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apps.controller.router, prefix="/api/v1")
app.include_router(auth.controller.router, prefix="/api/v1")
app.include_router(categories.controller.router, prefix="/api/v1")
app.include_router(integrations.controller.router, prefix="/api/v1")
app.include_router(permissions.controller.router, prefix="/api/v1")
app.include_router(platforms.controller.router, prefix="/api/v1")
app.include_router(public.controller.router, prefix="/api/v1")
app.include_router(roles.controller.router, prefix="/api/v1")
app.include_router(analytics.controller.router, prefix="/api/v1")
app.include_router(tags.controller.router, prefix="/api/v1")
app.include_router(users.controller.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to Applibry API Documentation!"}

handler = Mangum(app = app)
