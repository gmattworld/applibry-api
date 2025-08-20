import datetime
import uuid
from datetime import timedelta

from decouple import config
from fastapi import Depends
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from applibry_api.application.v1.auth.schema import RegisterSchema
from applibry_api.domain.entities.user import User
from applibry_api.domain.exceptions.base_exception import AppBadRequestException
from applibry_api.domain.utilities.cryptography import verify_password, hash_password
from applibry_api.infrastructure.persistence.database import get_db


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterSchema, code: str):
        result = await self.db.execute(
            select(User).filter(func.lower(User.email) == data.email.lower())
        )
        if result.scalar_one_or_none():
            raise AppBadRequestException("User with this email exists")

        entity = User(
            email=data.email,
            username=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            password_hash=hash_password(data.password),
            public_key=str(uuid.uuid4()),
            verification_code=hash_password(code),
            account_type=data.account_type,
            is_admin=False,
            is_active=True,
            is_verified=False,
            is_verified_at=None,
        )
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(func.lower(User.email) == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(func.lower(User.username) == username.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_public_key(self, public_key: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(User.public_key == public_key)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def initiate_password_reset(self, email: str, code: str):
        entity = await self.get_user_by_email(email)
        if not entity:
            raise AppBadRequestException("Account with the provided email does not exist")

        entity.password_reset_requested = True
        entity.password_reset_code = hash_password(code)
        if not entity.public_key:
            entity.public_key = str(uuid.uuid4())
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def verify_password_reset(self, code: str, email: str):
        user = await self.get_user_by_email(email)
        if not user:
            raise AppBadRequestException("User not found")

        if not verify_password(code, user.password_reset_code):
            raise AppBadRequestException("Incorrect code")
        return user

    async def reset_password(self, new_password: str, email: str):
        user = await self.get_user_by_email(email)
        if not user:
            raise AppBadRequestException("User not found")

        user.password_reset_requested = False
        user.password_hash = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, current_password: str, new_password: str, email: str):
        user = await self.get_user_by_email(email)
        if not user:
            raise AppBadRequestException("User not found")

        if not verify_password(current_password, user.password_hash):
            raise AppBadRequestException("Incorrect password")

        user.password_hash = hash_password(new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, username: str, password: str) -> User:
        user = await self.get_user_by_username(username)
        if not user:
            raise AppBadRequestException("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise AppBadRequestException("Invalid credentials")

        return user

    async def refresh(self, refresh_token: str) -> User:
        payload = jwt.decode(
            refresh_token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")]
        )
        if payload.get("type") != "refresh":
            raise AppBadRequestException("Invalid credentials")

        user_id = payload.get("sid")
        user = await self.get_user_by_id(user_id)
        if not user:
            raise AppBadRequestException("Invalid credentials")
        return user

    async def verify(self, code: str, public_key: str):
        user = await self.get_user_by_public_key(public_key)
        if not user:
            raise AppBadRequestException("User not found")

        if not verify_password(code, user.verification_code):
            raise AppBadRequestException("Incorrect code")

        user.email_confirmed = True
        user.is_verified = True
        user.is_verified_at = datetime.datetime.now()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def verify_preference_config(self, email: str):
        user = await self.get_user_by_email(email)
        if not user:
            raise AppBadRequestException("User not found")

        user.is_preference_configured = True
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def regenerate_email_verification_code(self, code: str, public_key: str):
        entity = await self.get_user_by_public_key(public_key)
        if not entity:
            raise AppBadRequestException("User not found")

        entity.verification_code = hash_password(code)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity


    async def generate_token(self, data: User, expires_delta: timedelta, _type: str = "access"):
        encode = {
            "sub": data.username,
            "sid": str(data.id),  # user id
            "exp": datetime.datetime.utcnow() + expires_delta,  # expiration time
            "iat": datetime.datetime.utcnow(),  # issued at time
            "nbf": datetime.datetime.utcnow(),  # not before time
            "type": _type,
        }
        return jwt.encode(encode, config("SECRET_KEY"), algorithm=config("ALGORITHM"))


def auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)