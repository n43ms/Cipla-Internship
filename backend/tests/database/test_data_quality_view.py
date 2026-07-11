from pathlib import Path


def test_data_quality_view_exposes_phase7_trust_metrics() -> None:
    sql = Path("database/views/mv_data_quality.sql").read_text(encoding="utf-8")

    for fragment in [
        "latest_ingestion_run_id",
        "source_file_count",
        "loaded_file_count",
        "rows_seen",
        "rows_loaded",
        "rows_skipped",
        "validation_error_count",
        "validation_warning_count",
        "match_coverage",
        "pcode_coverage",
        "rcpa_coverage",
        "rcpa_manual_mapping_count",
        "rcpa_system_mapping_count",
        "rcpa_source_mapping_count",
        "rcpa_unknown_mapping_count",
        "rcpa_covered_month_start",
        "rcpa_covered_month_end",
        "missing_fx_count",
        "provisional_fx_count",
        "serial_month_parse_count",
        "btu_btc_reconciliation_issue_count",
        "missing_confirmed_amount_count",
        "request_workflow_coverage",
        "post_workflow_coverage",
        "intervention_type_coverage",
        "unmatched_event_count",
        "derived_snapshot_count",
        "actual_attendance_missing_pcode_count",
        "unallocated_doctor_spend_usd",
    ]:
        assert fragment in sql


def test_data_quality_view_integrates_budget_doctor_workflow_and_unmatched_inputs() -> None:
    sql = Path("database/views/mv_data_quality.sql").read_text(encoding="utf-8")

    for fragment in [
        "from mv_budget_utilization",
        "from mv_doctor_roi",
        "from execution_requests",
        "from mv_unmatched_events",
        "from validation_errors",
        "from source_files",
        "from request_doctors",
    ]:
        assert fragment in sql
