from pathlib import Path


def test_execution_governance_view_sql_files_define_required_views() -> None:
    expected = {
        "mv_execution_kpis.sql": ["planned_events", "match_coverage", "snapshot_source_counts", "sum(planned_total_hcps)"],
        "mv_unmatched_events.sql": ["candidate_match", "confidence", "source_references"],
        "mv_execution_event_matrix.sql": ["planned_hcps", "engaged_hcps", "source_derivation_note"],
        "mv_workflow_governance.sql": ["pending_request_count", "pending_report_count", "expense_submitted_flag"],
        "mv_intervention_mix.sql": ["intervention_type", "request_count", "fx_rate_status"],
    }
    for filename, fragments in expected.items():
        sql = Path("database/views", filename).read_text(encoding="utf-8")
        assert "create materialized view" in sql
        for fragment in fragments:
            assert fragment in sql


def test_execution_governance_migration_installs_views_and_indexes() -> None:
    migration_sql = Path("database/migrations/versions/0010_execution_governance_views.py").read_text(encoding="utf-8")
    for name in ["mv_execution_kpis", "mv_unmatched_events", "mv_workflow_governance", "mv_intervention_mix"]:
        assert name in migration_sql
    assert "ix_event_matches_status" in migration_sql


def test_phase4_fix_migration_installs_execution_event_matrix() -> None:
    migration_sql = Path("database/migrations/versions/0011_phase4_execution_matrix_fixes.py").read_text(encoding="utf-8")

    assert "mv_execution_event_matrix" in migration_sql
    assert "ix_mv_execution_event_matrix_country_month" in migration_sql
