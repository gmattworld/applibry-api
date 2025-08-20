from datetime import timedelta
from decouple import config
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = config("DATABASE_URL", default="")

    # Environment
    IS_PROD: bool = config("IS_PROD", default=True, cast=bool)
    BASE_DOMAIN: str = config("BASE_DOMAIN", default="phareztech.com")

    # Security
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRES_IN_MINS: int = config(
        "ACCESS_TOKEN_EXPIRES_IN_MINS", default=30, cast=int)
    REFRESH_TOKEN_EXPIRES_IN_MINS: int = config(
        "REFRESH_TOKEN_EXPIRES_IN_MINS", default=60 * 24 * 7, cast=int)  # 7 days

    # AWS
    AWS__BUCKET_NAME: str = config("AWS__BUCKET_NAME", default="")
    AWS__REGION: str = config("AWS__REGION", default="")
    AWS__ACCESS_KEY: str = config("AWS__ACCESS_KEY", default="")
    AWS__SECRET_KEY: str = config("AWS__SECRET_KEY", default="")
    AWS__SES_SENDER: str = config("AWS__SES_SENDER", default="")

    # OpenAI
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")
    ORGANIZATION_ID: str = config("ORGANIZATION_ID", default="")
    PROJECT_ID: str = config("PROJECT_ID", default="")

    # NattyPad
    NATTYPAD_BASE_URL: str = config("NATTYPAD_BASE_URL", default="")
    NATTYPAD_CLIENT_ID: str = config("NATTYPAD_CLIENT_ID", default="")
    NATTYPAD_CLIENT_SECRET: str = config("NATTYPAD_CLIENT_SECRET", default="")

    # Email
    MAIL_USERNAME: str = config("MAIL_USERNAME", default="")
    MAIL_PASSWORD: str = config("MAIL_PASSWORD", default="")
    MAIL_FROM: str = config("MAIL_FROM", default="")
    MAIL_FROM_NAME: str = config("MAIL_FROM_NAME", default="")
    MAIL_PORT: int = config("MAIL_PORT", default=587, cast=int)
    MAIL_SERVER: str = config("MAIL_SERVER", default="")
    MAIL_STARTTLS: bool = config("MAIL_STARTTLS", default=True, cast=bool)
    MAIL_SSL_TLS: bool = config("MAIL_SSL_TLS", default=False, cast=bool)
    USE_CREDENTIALS: bool = config("USE_CREDENTIALS", default=True, cast=bool)
    VALIDATE_CERTS: bool = config("VALIDATE_CERTS", default=True, cast=bool)

    # Frontend
    FRONTEND_URL: str = config("FRONTEND_URL", default="http://localhost:3000")

    # Security
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = config(
        "PASSWORD_RESET_TOKEN_EXPIRE_HOURS", default=24, cast=int)
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = config(
        "VERIFICATION_TOKEN_EXPIRE_HOURS", default=24, cast=int)

    # File Upload
    MAX_FILE_SIZE: int = config(
        "MAX_FILE_SIZE", default=5242880, cast=int)  # 5MB
    ALLOWED_EXTENSIONS: list = config(
        "ALLOWED_EXTENSIONS", default="jpg,jpeg,png,pdf", cast=lambda v: [s.strip() for s in v.split(',')])

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = config(
        "RATE_LIMIT_ENABLED", default=True, cast=bool)
    RATE_LIMIT_DEFAULT: str = config(
        "RATE_LIMIT_DEFAULT", default="100/minute")
    RATE_LIMIT_STORAGE_URI: str = config(
        "RATE_LIMIT_STORAGE_URI", default="memory://")
    RATE_LIMIT_STRATEGY: str = config(
        "RATE_LIMIT_STRATEGY", default="fixed-window")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure log directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)
