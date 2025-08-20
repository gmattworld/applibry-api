from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.platform import Platform
from applibry_api.domain.entities.tag import Tag
from applibry_api.domain.enums.lookup_type import LookupType


class LookupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_lookups(self, lookup_type: LookupType):
        entity_map = {
            LookupType.CATEGORY: Category,
            LookupType.TAG: Tag,
            LookupType.PLATFORM: Platform,
        }

        entity = entity_map.get(lookup_type)
        if not entity:
            return []

        stmt = select(entity).where(entity.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all() 