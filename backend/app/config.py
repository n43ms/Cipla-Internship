from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SECRET_FIELD_NAMES = ("key", "token", "secret", "password", "url")


class Settings(BaseSettings):
    """Backend runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    deployment_mode: str = Field(default="local", alias="DEPLOYMENT_MODE")
    database_url: str = Field(default="", alias="DATABASE_URL")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_project_ref: str = Field(default="", alias="SUPABASE_PROJECT_REF")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    demo_access_mode: str = Field(default="local", alias="DEMO_ACCESS_MODE")
    demo_shared_password: str = Field(default="", alias="DEMO_SHARED_PASSWORD")
    company_lkr_per_usd: float = Field(default=310.0, alias="COMPANY_LKR_PER_USD")
    ai_provider: str = Field(default="null", alias="AI_PROVIDER")
    ai_api_key: str = Field(default="", alias="AI_API_KEY")
    ai_model: str = Field(default="", alias="AI_MODEL")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def redacted_dict(self) -> dict[str, object]:
        values = self.model_dump()
        for key in list(values):
            if any(marker in key.lower() for marker in SECRET_FIELD_NAMES):
                values[key] = "***" if values[key] else ""
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()
