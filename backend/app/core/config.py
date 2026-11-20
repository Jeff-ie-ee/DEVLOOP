
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DEVLOOP API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database configuration
    DATABASE_URL: str = (
        "postgresql+pg8000://devloop_admin:change_me@localhost:5433/devloop_db"
    )

    # JWT authentication configuration
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Refresh-token configuration
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Local development only. Enable HTTPS and set this to True in production.
    REFRESH_TOKEN_COOKIE_SECURE: bool = False
    REFRESH_TOKEN_COOKIE_NAME: str = "devloop_refresh"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
