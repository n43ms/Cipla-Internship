from backend.app.config import Settings
from ingestion.config import IngestionSettings


def test_backend_settings_redact_secrets() -> None:
    settings = Settings(DATABASE_URL="postgresql://user:secret@example/db", AI_API_KEY="secret")
    redacted = settings.redacted_dict()

    assert redacted["database_url"] == "***"
    assert redacted["ai_api_key"] == "***"


def test_ingestion_settings_redact_database_url() -> None:
    settings = IngestionSettings(DATABASE_URL="postgresql://user:secret@example/db")

    assert settings.redacted_dict()["database_url"] == "***"


def test_company_lkr_rate_defaults_to_july_10_official_rate() -> None:
    assert Settings(_env_file=None).company_lkr_per_usd == 368.90
    assert IngestionSettings(_env_file=None).company_lkr_per_usd == 368.90
