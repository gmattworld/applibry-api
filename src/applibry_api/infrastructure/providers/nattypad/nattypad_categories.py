from uuid import UUID

import httpx
from aiocache import cached
from decouple import config

from applibry_api.infrastructure.providers.nattypad.nattypad_auth import authenticate

from applibry_api.infrastructure.providers.nattypad.schemas.app_schema import AppCategorySchema, AppResponseSchemaExt, AppResponseSchema

base_url = config('NATTYPAD_BASE_URL')

@cached(ttl=3600)
async def get_categories(search: str, page: int, per_page: int) -> AppResponseSchemaExt[AppCategorySchema]:
    api_url = f"{base_url}/apps/categories?page={page}&per_page={per_page}"

    if search:
        api_url = f"{api_url}&search={search}"

    token = await authenticate()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return AppResponseSchemaExt[AppCategorySchema](
                data=[AppCategorySchema.model_validate(item) for item in data["data"]],
                success=True,
                current_page=data["current_page"],
                page_size=data["page_size"],
                total=data["total"],
                message=data["message"]
            )

    except httpx.HTTPStatusError as http_err:
        raise
    except Exception as err:
        raise


async def get_category(id: UUID) -> AppResponseSchema[AppCategorySchema]:
    api_url = f"{base_url}/apps/categories/{id}"
    token = await authenticate()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return AppResponseSchema[AppCategorySchema](
                data=AppCategorySchema.model_validate(data["data"]),
                success=True,
                message=data["message"]
            )

    except httpx.HTTPStatusError as http_err:
        raise
    except Exception as err:
        raise
