from typing import Optional, Dict
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.categories.schema import (
    CreateCategorySchema,
    UpdateCategorySchema,
)
from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.user import User
from applibry_api.domain.exceptions.base_exception import (
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.domain.utilities.slugify import generate_slug
from applibry_api.infrastructure.persistence.database import get_db


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_categories(
        self, skip: int, limit: int, search: Optional[str] = None
    ):
        stmt = select(Category)
        if search:
            stmt = stmt.filter(Category.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Category.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_categories_lookup(self):
        stmt = select(Category).filter(
            and_(Category.is_deleted == False, Category.is_active == True)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_category(self, _id: UUID) -> Category:
        result = await self.db.execute(select(Category).filter(Category.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("Category not found")
        return entity

    async def get_user_categories(
        self,
        decoded_token: dict[str, str],
        skip: int,
        limit: int,
        search: Optional[str] = None,
    ):
        user_id = decoded_token.get("sid")
        if not user_id:
            return {"total": 0, "data": []}

        stmt = select(Category).join(Category.users).filter(User.id == user_id)

        if search:
            stmt = stmt.filter(Category.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Category.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def create_category(
        self, decoded_token: Dict[str, str], data: CreateCategorySchema
    ):
        result = await self.db.execute(
            select(Category).filter(Category.name == data.name)
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Category with this name already exists")

        entity = Category(**data.model_dump())
        entity.created_by_id = decoded_token.get("sid")
        entity.slug = await self.get_unique_slug(entity.name)

        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_category(
        self, decoded_token: Dict[str, str], _id: UUID, data: UpdateCategorySchema
    ):
        result = await self.db.execute(
            select(Category).filter(and_(Category.name == data.name, Category.id != _id))
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Category with the same name already exists")

        entity = await self.get_category(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.slug = await self.get_unique_slug(entity.name, _id)
        entity.last_updated_by_id = decoded_token.get("sid")
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_category(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_category(self, _id: UUID):
        entity = await self.get_category(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

    async def get_unique_slug(self, name: str, category_id: Optional[UUID] = None):
        slug = generate_slug(name)
        counter = 1
        while True:
            stmt = select(Category).filter(Category.slug == slug)
            if category_id:
                stmt = stmt.filter(Category.id != category_id)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            slug = f"{slug}-{counter}"
            counter += 1
        return slug

def category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(db)