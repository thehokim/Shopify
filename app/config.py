from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Shopify Clone API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: Optional[str] = "development"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/shopify"
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://admin:admin@rabbitmq:5672"
    RABBITMQ_DEFAULT_USER: Optional[str] = None
    RABBITMQ_DEFAULT_PASS: Optional[str] = None

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_PRODUCTS: str = "products"
    MINIO_BUCKET_AVATARS: str = "avatars"

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    ELASTICSEARCH_INDEX_PRODUCTS: str = "products"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Email/SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None

    # Payment Gateways
    STRIPE_SECRET_KEY: Optional[str] = None
    PAYME_MERCHANT_ID: Optional[str] = None
    CLICK_SERVICE_ID: Optional[str] = None

    # Telegram Bots
    MONITORING_BOT_TOKEN: str = "8580271436:AAEEcQTRs5Xk5tjEDZq5MOPnuPNsYloSrBQ"
    MARKETPLACE_BOT_TOKEN: str = "8364684871:AAHqNgWEAk-B2xu_DCJUsKX0t18lW11-TPM"
    TELEGRAM_CHAT_ID: int = 5008138452
    
    # Telegram Mini App
    WEBAPP_URL: str = "https://shopifyforvercel.vercel.app/"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # ВАЖНО: Игнорировать неизвестные поля из .env


@lru_cache()
def get_settings():
    """Get cached settings instance"""
    return Settings()


# Create instance for import
settings = get_settings()