from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.platforms.schema import (
    CreatePlatformSchema,
    UpdatePlatformSchema,
)
from applibry_api.domain.entities.platform import Platform
from applibry_api.domain.exceptions.base_exception import (
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.infrastructure.persistence.database import get_db


class PlatformService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_platforms(
        self, skip: int, limit: int, search: Optional[str] = None
    ):
        stmt = select(Platform)
        if search:
            stmt = stmt.filter(Platform.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Platform.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_platforms_lookup(self):
        stmt = select(Platform).filter(
            and_(Platform.is_deleted != True, Platform.is_active)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_platform(self, _id: UUID) -> Platform:
        result = await self.db.execute(select(Platform).filter(Platform.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("Platform not found")
        return entity

    async def create_platform(
        self, decoded_token: dict[str, str], data: CreatePlatformSchema
    ):
        result = await self.db.execute(
            select(Platform).filter(Platform.name == data.name)
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Platform already exists")

        entity = Platform(**data.model_dump())
        entity.created_by_id = decoded_token.get("sid")
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_platform(
        self, decoded_token: dict[str, str], _id: UUID, data: UpdatePlatformSchema
    ):
        result = await self.db.execute(
            select(Platform).filter(and_(Platform.name == data.name, Platform.id != _id))
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Platform with same name exists")

        entity = await self.get_platform(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
            
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_platform(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_platform(self, _id: UUID):
        entity = await self.get_platform(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

def platform_service(db: AsyncSession = Depends(get_db)) -> PlatformService:
    return PlatformService(db)