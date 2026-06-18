from pathlib import Path


def test_budget_view_defines_phase5_financial_semantics() -> None:
    sql = Path("database/views/mv_budget_utilization.sql").read_text(encoding="utf-8")

    for fragment in [
        "planned_budget_usd",
        "confirmed_contracted_amount_local",
        "direct_hcp_btu_spend_local",
        "overhead_btc_spend_local",
        "btu_btc_reconciliation_status",
        "spend_without_plan",
        "plan_without_spend",
    ]:
        assert fragment in sql


def test_doctor_roi_view_defines_phase6_segments_and_quadrants() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    for fragment in [
        "country_id, pcode_normalized",
        "engagement_count",
        "cipla_prescription_qty",
        "spend_per_cipla_prescription_usd",
        "roi_segment",
        "quadrant_label",
        "dark_horse_flag",
    ]:
        assert fragment in sql


def test_data_quality_view_defines_phase7_coverage_flags() -> None:
    sql = Path("database/views/mv_data_quality.sql").read_text(encoding="utf-8")

    for fragment in [
        "validation_error_count",
        "match_coverage",
        "pcode_coverage",
        "rcpa_coverage",
        "missing_fx_count",
        "btu_btc_reconciliation_issue_count",
        "intervention_type_coverage",
        "derived_snapshot_count",
    ]:
        assert fragment in sql


def test_phase5_to_7_migrations_install_views_in_order() -> None:
    budget = Path("database/migrations/versions/0016_budget_finance_view.py").read_text(encoding="utf-8")
    doctor = Path("database/migrations/versions/0017_doctor_roi_quadrant_view.py").read_text(encoding="utf-8")
    quality = Path("database/migrations/versions/0018_data_quality_view.py").read_text(encoding="utf-8")

    assert "0015_snapshot_provenance" in budget
    assert "0016_budget_finance_view" in doctor
    assert "0017_doctor_roi_quadrant_view" in quality
    assert "mv_budget_utilization" in budget
    assert "mv_doctor_roi" in doctor
    assert "mv_data_quality" in quality
