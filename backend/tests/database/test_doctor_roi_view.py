from pathlib import Path


def test_doctor_roi_view_exposes_engagement_spend_and_rcpa_contract() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    for fragment in [
        "attendance_type = 'actual'",
        "pcode_normalized",
        "engagement_count",
        "first_engagement_date",
        "last_engagement_date",
        "direct_hcp_btu_spend_usd",
        "overhead_btc_spend_usd",
        "total_roi_spend_usd",
        "cipla_prescription_qty",
        "competitor_prescription_qty",
        "total_prescription_qty",
        "cipla_share_qty",
        "spend_per_cipla_prescription_usd",
        "has_rcpa",
    ]:
        assert fragment in sql


def test_doctor_roi_view_allocates_request_spend_across_parsed_actual_pcodes() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    assert "request_actual_counts" in sql
    assert "count(distinct pcode_normalized)" in sql
    assert "actual_btu_expense_usd / nullif(rac.doctor_count, 0)" in sql
    assert "actual_btc_expense_usd / nullif(rac.doctor_count, 0)" in sql
    assert "actual_total_expense_usd / nullif(rac.doctor_count, 0)" in sql
