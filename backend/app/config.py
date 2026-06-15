from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    database_url: str = Field(default="", alias="DATABASE_URL")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    ai_provider: str = Field(default="null", alias="AI_PROVIDER")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_model: str = Field(default="", alias="AI_MODEL")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
