from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.tags.schema import CreateTagSchema, UpdateTagSchema
from applibry_api.domain.entities.tag import Tag
from applibry_api.domain.exceptions.base_exception import (
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.infrastructure.persistence.database import get_db


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tags(self, skip: int, limit: int, search: Optional[str] = None):
        stmt = select(Tag)
        if search:
            stmt = stmt.filter(Tag.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Tag.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_tags_lookup(self):
        stmt = select(Tag).filter(and_(Tag.is_deleted != True, Tag.is_active))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tag(self, _id: UUID) -> Tag:
        result = await self.db.execute(select(Tag).filter(Tag.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("Tag not found")
        return entity

    async def create_tag(self, decoded_token: dict[str, str], data: CreateTagSchema):
        result = await self.db.execute(select(Tag).filter(Tag.name == data.name))
        if result.scalar_one_or_none():
            raise AppBadRequestException("Tag already exists")

        entity = Tag(**data.model_dump())
        entity.created_by_id = decoded_token.get("sid")
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_tag(self, _id: UUID, data: UpdateTagSchema):
        result = await self.db.execute(
            select(Tag).filter(and_(Tag.name == data.name, Tag.id != _id))
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Tag with same name exists")

        entity = await self.get_tag(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_tag(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_tag(self, _id: UUID):
        entity = await self.get_tag(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

def tag_service(db: AsyncSession = Depends(get_db)) -> TagService:
    return TagService(db)