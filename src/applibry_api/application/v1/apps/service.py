import base64
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from applibry_api.application.v1.apps.schema import CreateAppSchema, UpdateAppSchema
from applibry_api.domain.entities.app import App
from applibry_api.domain.enums.app_status import AppStatus
from applibry_api.domain.entities.category import Category
from applibry_api.domain.entities.platform import Platform
from applibry_api.domain.entities.tag import Tag
from applibry_api.domain.entities.user import User
from applibry_api.domain.entities.user_app import user_apps
from applibry_api.domain.exceptions.base_exception import AppBadRequestException, AppNotFoundException
from applibry_api.domain.utilities import file_manager
from applibry_api.domain.utilities.slugify import generate_slug
from applibry_api.infrastructure.persistence.database import get_db


def encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode()

def decode_cursor(cursor: str) -> str:
    return base64.urlsafe_b64decode(cursor.encode()).decode()

class AppService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_apps(
        self,
        decoded_token: dict[str, str],
        limit: int = 10,
        cursor: Optional[str] = None,
        personalised: bool = True,
        search: Optional[str] = None,
        category: Optional[str] = None
    ):
        user_id = decoded_token.get("sid")
        stmt = select(App).options(selectinload(App.category), selectinload(App.users), selectinload(App.tags), selectinload(App.platforms))

        if personalised and user_id:
            stmt = (
                stmt.join(App.category)
                .join(Category.users)
                .filter(User.id == user_id)
                .filter(~App.users.any(User.id == user_id))
            )

        if search:
            stmt = stmt.filter(App.name.ilike(f"%{search}%"))

        if category:
            stmt = stmt.filter(App.category_id == UUID(category))

        if cursor:
            cursor_value = decode_cursor(cursor)
            stmt = stmt.filter(App.name > cursor_value)

        stmt = stmt.order_by(App.name).limit(limit + 1)
        result = await self.db.execute(stmt)
        results = result.scalars().all()

        next_cursor = None
        if len(results) > limit:
            next_cursor = encode_cursor(results[-2].name)
            results.pop()

        return {"data": results, "next_cursor": next_cursor}

    async def get_trending_apps(
        self,
        limit: int,
        category: Optional[str] = None,
        cursor: Optional[str] = None,
    ):
        stmt = select(App).filter(App.trending == True).options(selectinload(App.category), selectinload(App.users), selectinload(App.tags), selectinload(App.platforms))

        if category:
            stmt = stmt.filter(App.category_id == UUID(category))

        if cursor:
            cursor_value = decode_cursor(cursor)
            stmt = stmt.filter(App.name > cursor_value)

        stmt = stmt.order_by(App.name).limit(limit + 1)
        result = await self.db.execute(stmt)
        apps = result.scalars().all()

        next_cursor = None
        if len(apps) > limit:
            next_cursor = encode_cursor(apps[-2].name)
            apps.pop()

        return {"data": apps, "next_cursor": next_cursor}

    async def get_user_apps(
        self,
        decoded_token: dict[str, str],
        limit: int,
        cursor: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[UUID] = None,
    ):
        user_id = decoded_token.get("sid")
        if not user_id:
            return {"data": [], "next_cursor": None}

        user_app_alias = aliased(user_apps)

        stmt = (
            select(App, user_app_alias.c.created_at)
            .join(
                user_app_alias,
                and_(
                    user_app_alias.c.app_id == App.id,
                    user_app_alias.c.user_id == user_id,
                ),
            )
        )

        if search:
            stmt = stmt.filter(App.name.ilike(f"%{search}%"))

        if category:
            stmt = stmt.filter(App.category_id == category)

        if cursor:
            created_at_cursor, name_cursor = decode_cursor(cursor)
            stmt = stmt.filter(
                or_(
                    user_app_alias.c.created_at < created_at_cursor,
                    and_(
                        user_app_alias.c.created_at == created_at_cursor,
                        App.name > name_cursor,
                    ),
                )
            )

        stmt = stmt.order_by(user_app_alias.c.created_at.desc(), App.name.asc()).limit(limit + 1)
        result = await self.db.execute(stmt)
        rows = result.all()  # List[Tuple[App, created_at]]

        apps = [row[0] for row in rows]
        next_cursor = None
        if len(apps) > limit:
            last_row = rows[-2]
            next_cursor = encode_cursor((last_row[1].isoformat(), last_row[0].name))
            apps.pop()

        return {"data": apps, "next_cursor": next_cursor}






    async def get_apps_lookup(self):
        stmt = select(App).filter(and_(not App.is_deleted, App.is_active))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_app(self, slug: str) -> App:
        stmt = select(App).filter(App.slug == slug).options(selectinload(App.category), selectinload(App.users), selectinload(App.tags), selectinload(App.platforms))
        result = await self.db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("App not found")
        return entity

    async def get_app_by_id(self, _id: UUID) -> App:
        stmt = select(App).filter(App.id == _id)
        result = await self.db.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            raise AppNotFoundException("App not found")
        return entity

    async def create_app(
        self, decoded_token: dict[str, str], data: CreateAppSchema
    ):
        result = await self.db.execute(select(App).filter(App.name == data.name))
        if result.scalar_one_or_none():
            raise AppBadRequestException("App with same name exists")

        category_result = await self.db.execute(
            select(Category).filter(Category.id == data.category_id)
        )
        category = category_result.scalar_one_or_none()
        if not category:
            raise AppNotFoundException("Category not found")

        icon_url = await file_manager.upload_to_s3(data.icon)
        banner_url = await file_manager.upload_to_s3(data.banner)

        entity = App(
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            slug=await self.get_unique_slug(data.name),
            website=data.website,
            pricing_model=data.pricing_model,
            price=data.price,
            brief=data.brief,
            status=data.status,
            meta_title=data.meta_title,
            meta_keywords=data.meta_keywords,
            meta_description=data.meta_description,
            created_by_id=decoded_token.get("sid"),
            icon=icon_url,
            banner=banner_url,
        )

        if data.tags:
            tags_result = await self.db.execute(select(Tag).where(Tag.id.in_(data.tags)))
            entity.tags = tags_result.scalars().all()

        if data.platforms:
            platforms_result = await self.db.execute(select(Platform).where(Platform.id.in_(data.platforms)))
            entity.platforms = platforms_result.scalars().all()

        self.db.add(entity)
        category.app_count += 1
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update_app(
        self, decoded_token: dict[str, str], _id: UUID, data: UpdateAppSchema
    ):
        result = await self.db.execute(
            select(App).filter(and_(App.name == data.name, App.id != _id))
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("App with same name exists")

        category_result = await self.db.execute(
            select(Category).filter(Category.id == data.category_id)
        )
        category = category_result.scalar_one_or_none()
        if not category:
            raise AppNotFoundException("Category not found")

        entity = await self.get_app_by_id(_id)
        old_category_id = entity.category_id
        update_category_count = data.category_id != old_category_id

        if data.icon and data.icon != entity.icon:
            entity.icon = await file_manager.upload_to_s3(data.icon)

        if data.banner and data.banner != entity.banner:
            entity.banner = await file_manager.upload_to_s3(data.banner)

        entity.name = data.name
        entity.description = data.description
        entity.category_id = data.category_id
        entity.slug = await self.get_unique_slug(entity.name, _id)
        entity.website = data.website
        entity.pricing_model = data.pricing_model
        entity.price = data.price
        entity.brief = data.brief
        entity.status = data.status
        entity.meta_title = data.meta_title
        entity.meta_keywords = data.meta_keywords
        entity.meta_description = data.meta_description
        entity.last_updated_by_id = decoded_token.get("sid")

        if data.tags:
            tags_result = await self.db.execute(select(Tag).where(Tag.id.in_(data.tags)))
            entity.tags = tags_result.scalars().all()

        if data.platforms:
            platforms_result = await self.db.execute(
                select(Platform).where(Platform.id.in_(data.platforms))
            )
            entity.platforms = platforms_result.scalars().all()

        if update_category_count:
            category.app_count += 1
            old_category_result = await self.db.execute(
                select(Category).filter(Category.id == old_category_id)
            )
            if old_category := old_category_result.scalar_one_or_none():
                old_category.app_count -= 1

        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def publish_app(self, decoded_token: dict[str, str], _id: UUID):
        entity = await self.get_app_by_id(_id)
        entity.status = AppStatus.PUBLISHED
        entity.published_at = datetime.utcnow()
        entity.last_updated_by_id = decoded_token.get("sid")
        entity.last_updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def revert_to_draft(self, decoded_token: dict[str, str], _id: UUID):
        entity = await self.get_app_by_id(_id)
        if entity.status != AppStatus.DRAFT:
            entity.status = AppStatus.DRAFT
            entity.last_updated_by_id = decoded_token.get("sid")
            entity.last_updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(entity)
        return entity

    async def agentic_app_generation(self, entity: App):
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def get_unique_slug(self, name: str, app_id: UUID | None = None):
        slug = generate_slug(name)
        counter = 1
        while True:
            stmt = select(App).filter(App.slug == slug)
            if app_id:
                stmt = stmt.filter(App.id != app_id)
            result = await self.db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            slug = f"{slug}-{counter}"
            counter += 1
        return slug


def app_service(db: AsyncSession = Depends(get_db)) -> AppService:
    return AppService(db)