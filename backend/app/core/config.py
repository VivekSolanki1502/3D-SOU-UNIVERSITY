import os
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SOU 3D Disha"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security / JWT
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = Field(min_length=12)
    POSTGRES_DB: str = "sou_disha_db"
    
    # Custom Database URI override (e.g., sqlite+aiosqlite:///./sou_disha.db for local dev or postgresql+asyncpg://...)
    DATABASE_URL: str | None = None

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = True
    REDIS_URL: str | None = None

    @property
    def ASYNC_REDIS_URL(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Seed User Credentials from Environment Variables
    SEED_ADMIN_EMAIL: str
    SEED_ADMIN_PASSWORD: str = Field(min_length=12)
    SEED_ADMIN_NAME: str

    SEED_FACULTY_EMAIL: str
    SEED_FACULTY_PASSWORD: str = Field(min_length=12)
    SEED_FACULTY_NAME: str

    SEED_STUDENT_EMAIL: str
    SEED_STUDENT_PASSWORD: str = Field(min_length=12)
    SEED_STUDENT_NAME: str

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_backend_cors_origins(cls, origins: List[str]) -> List[str]:
        normalized = [origin.strip().rstrip("/") for origin in origins]
        if any(not origin for origin in normalized) or "*" in normalized:
            raise ValueError("CORS origins must be explicit origins; wildcard origins are not allowed")
        return normalized

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
