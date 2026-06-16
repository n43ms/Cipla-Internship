from pathlib import Path


def test_migration_files_exist_in_expected_order(migration_files: list[str]) -> None:
    versions_dir = Path("database/migrations/versions")
    existing = [path.name for path in sorted(versions_dir.glob("*.py"))]

    for migration_file in migration_files:
        assert migration_file in existing


def test_seed_files_exist() -> None:
    for seed_file in [
        "countries.sql",
        "calendar_months.sql",
        "exchange_rates_static.sql",
    ]:
        assert Path("database/seeds", seed_file).exists()


def test_official_lkr_company_rate_seed_is_present() -> None:
    seed_sql = Path("database/seeds/exchange_rates_static.sql").read_text(encoding="utf-8")
    assert "'LKR'" in seed_sql
    assert "1.0 / 310.0" in seed_sql
    assert "'official'" in seed_sql
    assert "'company'" in seed_sql
