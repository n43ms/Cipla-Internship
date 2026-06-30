from pathlib import Path

from ingestion.validators.doctor_quality import cross_country_pcode_collisions, same_country_doctor_conflicts


def test_doctors_are_unique_by_country_scoped_pcode() -> None:
    migration = Path("database/migrations/versions/0004_canonical_tables.py").read_text(encoding="utf-8")

    assert "uq_doctors_country_pcode" in migration
    assert '"country_id", "pcode_normalized"' in migration


def test_cross_country_pcode_collision_reporting_is_country_scoped() -> None:
    rows = [
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A"},
        {"country": "Sri Lanka", "pcode_normalized": "1001", "doctor_name": "Dr B"},
        {"country": "Nepal", "pcode_normalized": "2002", "doctor_name": "Dr C"},
    ]

    assert cross_country_pcode_collisions(rows) == {"1001": ["Nepal", "Sri Lanka"]}


def test_same_country_doctor_conflicts_keep_pcode_key_visible() -> None:
    rows = [
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A"},
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A Alias"},
        {"country": "Sri Lanka", "pcode_normalized": "1001", "doctor_name": "Dr B"},
    ]

    conflicts = same_country_doctor_conflicts(rows)
    assert conflicts[("Nepal", "1001")] == ["Dr A", "Dr A Alias"]
