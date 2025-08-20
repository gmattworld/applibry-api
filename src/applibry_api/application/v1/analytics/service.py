from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.domain.entities.app import App
from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.permission import Permission
from applibry_api.domain.entities.platform import Platform
from applibry_api.domain.entities.role import Role
from applibry_api.domain.entities.tag import Tag
from applibry_api.domain.entities.user import User
from applibry_api.domain.entities.user_app import user_apps
from applibry_api.domain.entities.user_category import user_categories
from applibry_api.infrastructure.persistence.database import get_db


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_statistics(self, decoded_token: dict[str, str]):
        user_id = decoded_token.get("sid")

        my_libry_app_count_stmt = select(func.count()).where(user_apps.c.user_id == user_id)
        my_libry_app_count_result = await self.db.execute(my_libry_app_count_stmt)
        my_libry_app_count = my_libry_app_count_result.scalar_one()

        preference_count_stmt = select(func.count()).where(user_categories.c.user_id == user_id)
        preference_count_result = await self.db.execute(preference_count_stmt)
        preference_count = preference_count_result.scalar_one()

        return {
            "MylibryAppCount": my_libry_app_count,
            "PreferenceCount": preference_count,
            "InteractionCount": 0,
            "SubmissionCount": 0,
        }

    async def _get_entity_statistics(self, entity):
        active_stmt = select(func.count()).where(entity.is_active == True)
        active_result = await self.db.execute(active_stmt)
        active_count = active_result.scalar_one()

        inactive_stmt = select(func.count()).where(entity.is_active == False)
        inactive_result = await self.db.execute(inactive_stmt)
        inactive_count = inactive_result.scalar_one()

        return {
            "ActiveCount": active_count,
            "InactiveCount": inactive_count,
            "TotalCount": active_count + inactive_count,
        }

    async def get_category_statistics(self):
        return await self._get_entity_statistics(Category)

    async def get_app_statistics(self):
        return await self._get_entity_statistics(App)

    async def get_user_statistics(self):
        return await self._get_entity_statistics(User)

    async def get_role_statistics(self):
        return await self._get_entity_statistics(Role)

    async def get_permission_statistics(self):
        return await self._get_entity_statistics(Permission)

    async def get_platform_statistics(self):
        return await self._get_entity_statistics(Platform)

    async def get_tag_statistics(self):
        return await self._get_entity_statistics(Tag)


def analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)