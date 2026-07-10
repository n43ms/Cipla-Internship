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
    assert "1.0 / 368.90" in seed_sql
    assert "'NPR', 1.0 / 89.0" in seed_sql
    assert "'official'" in seed_sql
    assert "'company'" in seed_sql
    assert "public_market_rate" not in seed_sql


def test_phase_1_3_schema_completion_migration_contains_required_columns() -> None:
    migration_path = Path(
        "database/migrations/versions/0007_phase_1_3_schema_completion.py"
    )
    migration_sql = migration_path.read_text(encoding="utf-8")
    for column_name in [
        "planned_honorarium_hcps",
        "yp_total_doctors",
        "fx_rate_source",
        "confirmed_contracted_amount_usd",
        "direct_hcp_spend_local",
        "expense_confirmed_date",
        "first_seen_month_id",
        "speciality",
        "sku_detail",
    ]:
        assert column_name in migration_sql


def test_free_tier_rcpa_storage_migration_contains_summary_tables() -> None:
    migration_path = Path(
        "database/migrations/versions/0008_supabase_free_tier_rcpa_storage.py"
    )
    migration_sql = migration_path.read_text(encoding="utf-8")
    for table_name in [
        "rcpa_doctor_month_summary",
        "rcpa_doctor_brand_summary",
        "rcpa_country_brand_month_summary",
    ]:
        assert table_name in migration_sql
    assert "TRUNCATE TABLE rcpa_prescriptions" in migration_sql


def test_obsolete_rcpa_prescriptions_table_is_dropped_by_head_migration() -> None:
    migration_path = Path(
        "database/migrations/versions/0009_drop_obsolete_rcpa_prescriptions.py"
    )
    migration_sql = migration_path.read_text(encoding="utf-8")
    assert 'op.drop_table("rcpa_prescriptions")' in migration_sql
    for table_name in [
        "rcpa_doctor_month_summary",
        "rcpa_doctor_brand_summary",
        "rcpa_country_brand_month_summary",
    ]:
        assert table_name not in migration_sql


def test_execution_governance_migration_file_exists(migration_files: list[str]) -> None:
    assert "0010_execution_governance_views.py" in migration_files


def test_phase4_repair_migrations_are_tracked(migration_files: list[str]) -> None:
    assert "0011_phase4_execution_matrix_fixes.py" in migration_files
    assert "0012_phase4_real_data_repairs.py" in migration_files
