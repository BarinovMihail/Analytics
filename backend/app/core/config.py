from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Procurement Analytics API"
    environment: str = "development"
    debug: bool = False

    mysql_host: str = "db"
    mysql_port: int = 3306
    mysql_user: str = "procurement"
    mysql_password: str = "procurement"
    mysql_database: str = "procurement_db"
    mysql_charset: str = "utf8mb4"
    database_url: str | None = None

    cors_origins_raw: str = Field(default="http://localhost:3000,http://localhost:5173")
    upload_max_size_mb: int = 20
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset={self.mysql_charset}"
        )

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
