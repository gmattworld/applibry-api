from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jose import jwt

from applibry_api.domain.utilities.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Ensure the database URL uses asyncpg
if not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(settings.DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=300, pool_timeout=30)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autocommit=False, autoflush=False
)

Base = declarative_base()


async def get_db():
    async with async_session() as session:
        yield session



def verify_token(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
