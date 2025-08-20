import asyncio

import httpx
from aiocache import cached, Cache
from decouple import config

base_url = config('NATTYPAD_BASE_URL')
client_id = config('NATTYPAD_CLIENT_ID')
client_secret = config('NATTYPAD_CLIENT_SECRET')

cache = Cache(Cache.MEMORY)
auth_lock = asyncio.Lock()

@cached(ttl=3600, key="auth_token")
async def authenticate():
    async with auth_lock:
        cached_token = await cache.get("auth_token")
        if cached_token:
            return cached_token

        api_url = f"{base_url}/apps/login"
        data = {"client_id": client_id, "client_secret": client_secret}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                access_token = result["access_token"]

                # Store the token in the cache
                await cache.set("auth_token", access_token, ttl=3600)

                return access_token
        except httpx.HTTPStatusError as http_err:
            # Handle specific HTTP errors
            raise http_err
        except Exception as err:
            # Handle other possible errors
            raise err