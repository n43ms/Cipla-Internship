from pathlib import Path


def test_storage_budget_script_redacts_database_url_and_reports_headroom() -> None:
    script = Path("scripts/db_size_report.ps1").read_text(encoding="utf-8")

    assert "DATABASE_URL" in script
    assert "Database URL: [redacted]" in script
    assert "Estimated free-tier headroom" in script
    assert "FreeTierLimitMb" in script
    assert "PrintSqlOnly" in script


def test_storage_budget_runbook_contains_required_sql_sections() -> None:
    runbook = Path("docs/storage-budget.md").read_text(encoding="utf-8")

    for expected in [
        "pg_database_size",
        "pg_total_relation_size",
        "rcpa_doctor_month_summary",
        "mapping provenance",
        "materialized views",
        "ai_query_logs",
        "raw files stay out of Supabase",
    ]:
        assert expected in runbook
