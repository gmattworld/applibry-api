from uuid import UUID

import httpx
from decouple import config

from applibry_api.infrastructure.providers.nattypad.nattypad_auth import authenticate

from applibry_api.infrastructure.providers.nattypad.schemas.app_schema import AppQuoteSchema, AppResponseSchemaExt, AppResponseSchema

base_url = config('NATTYPAD_BASE_URL')

async def get_quotes(search: str, page: int, per_page: int) -> AppResponseSchemaExt[AppQuoteSchema]:
    api_url = f"{base_url}/apps/quotes?page={page}&per_page={per_page}"

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

            return AppResponseSchemaExt[AppQuoteSchema](
                data=[AppQuoteSchema.model_validate(item) for item in data["data"]],
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


async def get_quote(id: UUID) -> AppResponseSchema[AppQuoteSchema]:
    api_url = f"{base_url}/apps/quotes/{id}"
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

            return AppResponseSchema[AppQuoteSchema](
                data=AppQuoteSchema.model_validate(data["data"]),
                success=True,
                message=data["message"]
            )

    except httpx.HTTPStatusError as http_err:
        raise
    except Exception as err:
        raise
