from pathlib import Path


def test_sponsorship_outcome_view_exposes_engagement_economics_and_counts() -> None:
    sql = Path("database/views/mv_sponsorship_outcomes.sql").read_text(encoding="utf-8")

    for fragment in [
        "sponsorship_count",
        "paid_engagement_count",
        "no_fee_engagement_count",
        "paid_service_count",
        "contracted_amount_usd",
        "fmv_amount_usd",
        "contract_saving_usd",
        "doctor_attributable_expense_local",
        "known_engagement_investment_usd",
    ]:
        assert fragment in sql


def test_sponsorship_outcome_view_uses_pre_post_association_language_not_causality() -> None:
    sql = Path("database/views/mv_sponsorship_outcomes.sql").read_text(encoding="utf-8")

    for fragment in [
        "pre_window_cipla_rx_qty",
        "post_window_cipla_rx_qty",
        "associated_rx_movement_qty",
        "first_engagement_date",
        "latest_engagement_date",
    ]:
        assert fragment in sql
    assert "causal" not in sql.lower()
    assert "uplift" not in sql.lower()


def test_sponsorship_outcome_view_exposes_confidence_and_caveats() -> None:
    sql = Path("database/views/mv_sponsorship_outcomes.sql").read_text(encoding="utf-8")

    for fragment in [
        "evidence_confidence",
        "evidence_caveats",
        "insufficient_pre_window_rcpa",
        "insufficient_post_window_rcpa",
        "manual_rcpa_mapping_period",
        "amount_unavailable_not_counted_as_zero",
    ]:
        assert fragment in sql


def test_doctor_roi_view_uses_known_sponsorship_amounts_and_missing_amount_caveats() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    assert "contracted_engagement_amount_usd" in sql
    assert "coalesce(e.total_roi_spend_usd, 0) + coalesce(de.contracted_engagement_amount_usd, 0)" in sql
    assert "sponsorship_engagement_amount_missing_count" in sql
