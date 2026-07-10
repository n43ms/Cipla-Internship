from pathlib import Path


def test_territory_opportunity_view_uses_source_backed_fields() -> None:
    sql = Path("database/views/mv_territory_opportunity.sql").read_text(encoding="utf-8")

    assert "rcpa_doctor_month_summary" in sql
    assert "doctor_engagement_facts" in sql
    assert "territory_name" in sql
    assert "fs_hq" in sql
    assert "patch_name" in sql
    assert "source_caveats" in sql


def test_territory_opportunity_view_defines_deterministic_labels() -> None:
    sql = Path("database/views/mv_territory_opportunity.sql").read_text(encoding="utf-8")

    assert "'underserved'" in sql
    assert "'overserved'" in sql
    assert "'self_serving'" in sql
    assert "prescriptions_per_doctor" in sql
    assert "engagements_per_doctor" in sql
    assert "known_investment_usd" in sql
