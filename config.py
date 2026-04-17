"""Configuration settings for AkoweAI backend."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/akowe"
    sqlalchemy_echo: bool = False

    # Redis/Cache
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"

    # APIs
    claude_api_key: str = ""
    openai_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    twilio_whatsapp_number: str = ""  # Optional: if using Twilio for WhatsApp

    # Cloudinary (File Storage)
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Security
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # App
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    app_name: str = "AkoweAI"
    api_v1_str: str = "/api/v1"

    # Pagination defaults
    default_page_size: int = 50
    max_page_size: int = 100

    # File upload limits
    max_upload_size_mb: int = 100  # Max 100MB for files

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
