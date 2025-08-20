from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.roles.schema import CreateRoleSchema, UpdateRoleSchema
from applibry_api.domain.entities.permission import Permission
from applibry_api.domain.entities.role import Role
from applibry_api.domain.exceptions.base_exception import (
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.domain.utilities.slugify import generate_slug
from applibry_api.infrastructure.persistence.database import get_db


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_roles(self, skip: int, limit: int, search: Optional[str] = None):
        stmt = select(Role)
        if search:
            stmt = stmt.filter(Role.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(Role.name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_roles_lookup(self):
        stmt = select(Role).filter(
            and_(Role.is_deleted == False, Role.is_active == True)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_role(self, _id: UUID) -> Role:
        result = await self.db.execute(select(Role).filter(Role.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("Role not found")
        return entity

    async def create_role(self, decoded_token: dict[str, str], data: CreateRoleSchema):
        result = await self.db.execute(select(Role).filter(Role.name == data.name))
        if result.scalar_one_or_none():
            raise AppBadRequestException("Role with same name exists")

        entity = Role(
            name=data.name,
            description=data.description,
            is_system_role=data.is_system_role,
            created_by_id=decoded_token.get("sid"),
            code=await self.get_unique_code(data.name),
        )

        if data.permissions:
            permissions_result = await self.db.execute(
                select(Permission).where(Permission.id.in_(data.permissions))
            )
            entity.permissions = permissions_result.scalars().all()

        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_role(self, _id: UUID, data: UpdateRoleSchema):
        result = await self.db.execute(
            select(Role).filter(and_(Role.name == data.name, Role.id != _id))
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("Role with same name exists")

        entity = await self.get_role(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key != "permissions":
                setattr(entity, key, value)
        
        entity.code = await self.get_unique_code(entity.name, _id)

        if data.permissions:
            permissions_result = await self.db.execute(
                select(Permission).where(Permission.id.in_(data.permissions))
            )
            entity.permissions = permissions_result.scalars().all()

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_role(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_role(self, _id: UUID):
        entity = await self.get_role(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

    async def get_unique_code(self, name: str, role_id: Optional[UUID] = None):
        code = generate_slug(name)
        counter = 1
        while True:
            stmt = select(Role).filter(Role.code == code)
            if role_id:
                stmt = stmt.filter(Role.id != role_id)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            code = f"{code}-{counter}"
            counter += 1
        return code

def role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(db)
