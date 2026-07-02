from pathlib import Path


def test_execution_governance_view_sql_files_define_required_views() -> None:
    expected = {
        "mv_execution_kpis.sql": [
            "planned_events",
            "planned_events_with_executed_evidence",
            "executed_snapshot_count",
            "matched_engaged_hcps",
            "match_coverage",
            "snapshot_source_counts",
            "is_primary_phase4_scope",
        ],
        "mv_unmatched_events.sql": ["candidate_match", "confidence", "source_references", "unmatched_reason_code"],
        "mv_execution_event_matrix.sql": ["planned_hcps", "engaged_hcps", "source_derivation_note", "match_grain"],
        "mv_workflow_governance.sql": ["pending_request_count", "pending_report_count", "expense_submitted_flag", "is_primary_phase4_scope"],
        "mv_intervention_mix.sql": ["intervention_type", "request_count", "executed_request_count", "executed_snapshot_count", "action_due_snapshot_count", "matched_without_execution_count"],
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
    assert "phase4_analysis_scope.sql" in migration_sql
    assert "ix_event_matches_status" in migration_sql


def test_phase4_fix_migration_installs_execution_event_matrix() -> None:
    migration_sql = Path("database/migrations/versions/0011_phase4_execution_matrix_fixes.py").read_text(encoding="utf-8")

    assert "mv_execution_event_matrix" in migration_sql
    assert "ix_mv_execution_event_matrix_country_month" in migration_sql


def test_phase4_scope_quality_migration_installs_repairs() -> None:
    migration_sql = Path("database/migrations/versions/0013_phase4_scope_and_quality_repairs.py").read_text(encoding="utf-8")

    assert "unmatched_reason_code" in migration_sql
    assert "mv_latest_validation_errors.sql" in migration_sql
    assert "ix_mv_intervention_mix_scope" in migration_sql
    assert "ix_mv_workflow_governance_country_month" in migration_sql


def test_phase4_semantic_repair_migration_installs_final_scope_and_grain_repairs() -> None:
    migration_sql = Path("database/migrations/versions/0014_phase4_semantic_repairs.py").read_text(encoding="utf-8")

    assert "snapshot_only_no_matching_plan" in migration_sql
    assert "ix_mv_workflow_governance_scope" in migration_sql
    assert "refresh_dashboard_materialized_views" in migration_sql


def test_snapshot_provenance_migration_adds_derivation_metadata() -> None:
    migration_sql = Path("database/migrations/versions/0015_execution_snapshot_derivation_provenance.py").read_text(encoding="utf-8")
    matrix_sql = Path("database/views/mv_execution_event_matrix.sql").read_text(encoding="utf-8")

    assert "source_derivation_json" in migration_sql
    assert "contributing_request_ids" in migration_sql
    assert "snapshotDerivation" in matrix_sql
