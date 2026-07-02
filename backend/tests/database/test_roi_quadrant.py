from pathlib import Path


def test_roi_quadrant_view_uses_deterministic_segments_and_labels() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    for fragment in [
        "roi_segment",
        "quadrant_x",
        "quadrant_y",
        "quadrant_label",
        "high_value_unengaged",
        "high_value_engaged",
        "low_rx_high_spend",
        "no_rcpa",
        "insufficient_data",
        "low effort / high reward",
        "high effort / high reward",
        "high effort / low reward",
        "low effort / low reward",
        "insufficient data",
    ]:
        assert fragment in sql


def test_dark_horse_flags_require_rcpa_high_prescriptions_and_low_engagement() -> None:
    sql = Path("database/views/mv_doctor_roi.sql").read_text(encoding="utf-8")

    assert "dark_horse_flag" in sql
    assert "dark_horse_unengaged_flag" in sql
    assert "high_value_engaged_flag" in sql
    assert "m.has_rcpa" in sql
    assert "m.engagement_count = 0" in sql
    assert "m.cipla_prescription_qty >= coalesce(t.median_cipla_qty, 0)" in sql
