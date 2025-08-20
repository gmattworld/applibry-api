from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import and_, delete, func, literal, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.users.schema import (
    CreateUserSchema,
    InviteUserSchema,
    UpdateUserProfileSchema,
    UpdateUserSchema,
)
from applibry_api.domain.entities.user_category import user_categories
from applibry_api.domain.entities.app import App
from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.user import User
from applibry_api.domain.exceptions.base_exception import (
    AppAuthorizationException,
    AppBadRequestException,
    AppNotFoundException,
)
from applibry_api.infrastructure.persistence.database import get_db


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, skip: int, limit: int, search: Optional[str] = None):
        stmt = select(User)
        if search:
            stmt = stmt.filter(User.email.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        data_stmt = stmt.order_by(User.last_name).offset(skip).limit(limit)
        data_result = await self.db.execute(data_stmt)
        data = data_result.scalars().all()
        return {"total": total, "data": data}

    async def get_users_lookup(self):
        stmt = select(User).filter(and_(User.is_deleted == False, User.is_active == True))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user(self, _id: UUID) -> User:
        result = await self.db.execute(select(User).filter(User.id == _id))
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("User not found")
        return entity

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, data: CreateUserSchema):
        if await self.get_user_by_username(data.username):
            raise AppBadRequestException("User already exists")

        entity = User(**data.model_dump())
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def add_to_user_libry(self, decoded_token: dict[str, str], app_id: UUID):
        user = await self.get_user(decoded_token["sid"])
        result = await self.db.execute(select(App).filter(App.id == app_id))
        app = result.scalar_one_or_none()

        if not app:
            raise AppNotFoundException("App not found")
        if app in user.apps:
            raise AppBadRequestException("App already in preference")

        user.apps.append(app)
        app.subscribers += 1
        await self.db.commit()
        return {"message": "App successfully added", "app_id": str(app_id)}

    async def remove_from_user_libry(
        self, decoded_token: dict[str, str], app_id: UUID
    ):
        user = await self.get_user(decoded_token["sid"])
        result = await self.db.execute(select(App).filter(App.id == app_id))
        app = result.scalar_one_or_none()

        if not app:
            raise AppNotFoundException("App not found")
        if app not in user.apps:
            raise AppBadRequestException("App not in preference")

        user.apps.remove(app)
        app.subscribers -= 1
        await self.db.commit()
        return {"message": "App successfully removed", "app_id": str(app_id)}

    async def add_to_user_preference(self, decoded_token: dict[str, str], category_id: UUID):
        user_id = decoded_token["sid"]

        # Ensure category exists
        exists_stmt = select(literal(True)).select_from(Category).where(Category.id == category_id).limit(1)
        if not (await self.db.execute(exists_stmt)).scalar():
            raise AppNotFoundException("Category not found")

        # Upsert association (no duplicate)
        stmt = (
            insert(user_categories)
            .values(user_id=user_id, category_id=category_id)
            .on_conflict_do_nothing(index_elements=[user_categories.c.user_id, user_categories.c.category_id])
        )
        res = await self.db.execute(stmt)
        if res.rowcount == 0:
            raise AppBadRequestException("Preference already added")

        # Atomic counter increment
        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(subscribers=Category.__table__.c.subscribers + 1)
        )
        await self.db.commit()
        return {"message": "Preference successfully added", "category_id": str(category_id)}

    async def remove_from_user_preference(self, decoded_token: dict[str, str], category_id: UUID):
        user_id = decoded_token["sid"]

        # Ensure category exists
        exists_stmt = select(literal(True)).select_from(Category).where(Category.id == category_id).limit(1)
        if not (await self.db.execute(exists_stmt)).scalar():
            raise AppNotFoundException("Category not found")

        # Delete association
        del_res = await self.db.execute(
            delete(user_categories)
            .where(user_categories.c.user_id == user_id, user_categories.c.category_id == category_id)
        )
        if del_res.rowcount == 0:
            raise AppBadRequestException("Category not in preference")

        # Atomic counter decrement (floor at 0)
        await self.db.execute(
            update(Category)
            .where(Category.id == category_id, Category.subscribers > 0)
            .values(subscribers=Category.__table__.c.subscribers - 1)
        )
        await self.db.commit()
        return {"message": "Preference successfully removed", "category_id": str(category_id)}


    async def invite_user(self, data: InviteUserSchema):
        if await self.get_user_by_email(data.email):
            raise AppBadRequestException("User exists")

        entity = User(
            email=data.email,
            username=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            role_id=data.role_id,
            is_admin=True,
        )
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_user(self, _id: UUID, data: UpdateUserSchema):
        entity = await self.get_user(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def change_status(self, _id: UUID):
        entity = await self.get_user(_id)
        entity.is_active = not entity.is_active
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_user_profile(
        self, _id: UUID, data: UpdateUserProfileSchema
    ):
        entity = await self.get_user(_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_user(self, _id: UUID):
        entity = await self.get_user(_id)
        await self.db.delete(entity)
        await self.db.commit()
        return True

    async def get_current_user(self, decoded_token: dict[str, str]) -> User:
        username: str = decoded_token.get("sub")
        if username is None:
            raise AppAuthorizationException("Could not validate credentials")
        user = await self.get_user_by_username(username)
        if user is None:
            raise AppAuthorizationException("User not found")
        return user

def user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)