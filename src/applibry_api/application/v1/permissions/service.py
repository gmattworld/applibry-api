from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.permissions.schema import (
    CreatePermissionSchema,
    UpdatePermissionSchema,
)
from applibry_api.domain.entities.permission import Permission
from applibry_api.domain.exceptions.base_exception import (
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.domain.utilities.slugify import generate_slug
from applibry_api.infrastructure.persistence.database import get_db


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_permissions(
        self, skip: int, limit: int, search: Optional[str] = None
    ):
        stmt = select(Permission)
        if search:
            stmt = stmt.filter(Permission.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Permission.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_permissions_lookup(self):
        stmt = select(Permission).filter(
            and_(Permission.is_deleted == False, Permission.is_active == True)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_permission(self, _id: UUID) -> Permission:
        result = await self.db.execute(select(Permission).filter(Permission.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("Permission not found")
        return entity

    async def create_permission(
        self, decoded_token: dict[str, str], data: CreatePermissionSchema
    ):
        result = await self.db.execute(
            select(Permission).filter(Permission.name == data.name)
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Permission with same name exists")

        entity = Permission(**data.model_dump())
        entity.code = await self.get_unique_code(entity.name)
        entity.created_by_id = decoded_token.get("sid")
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_permission(self, _id: UUID, data: UpdatePermissionSchema):
        result = await self.db.execute(
            select(Permission).filter(
                and_(Permission.name == data.name, Permission.id != _id)
            )
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Permission with same name exists")

        entity = await self.get_permission(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
            
        entity.code = await self.get_unique_code(entity.name, _id)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_permission(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_permission(self, _id: UUID):
        entity = await self.get_permission(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

    async def get_unique_code(self, name: str, permission_id: Optional[UUID] = None):
        code = generate_slug(name)
        counter = 1
        while True:
            stmt = select(Permission).filter(Permission.code == code)
            if permission_id:
                stmt = stmt.filter(Permission.id != permission_id)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            code = f"{code}-{counter}"
            counter += 1
        return code

def permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(db)