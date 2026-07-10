from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    """Settings for local workbook ingestion."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(default="", alias="DATABASE_URL")
    data_dir: Path = Field(default=Path("data/raw"), alias="DATA_DIR")
    processed_data_dir: Path = Field(default=Path("data/processed"), alias="PROCESSED_DATA_DIR")
    reports_dir: Path = Field(default=Path("data/reports"), alias="REPORTS_DIR")
    company_lkr_per_usd: float = Field(default=368.90, alias="COMPANY_LKR_PER_USD")

    def redacted_dict(self) -> dict[str, object]:
        values = self.model_dump()
        if values.get("database_url"):
            values["database_url"] = "***"
        return values


@lru_cache
def get_settings() -> IngestionSettings:
    return IngestionSettings()
