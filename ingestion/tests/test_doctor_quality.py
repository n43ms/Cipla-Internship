from ingestion.validators.doctor_quality import cross_country_pcode_collisions, same_country_doctor_conflicts


def test_cross_country_pcode_collisions_are_reported_without_rejecting_country_scope() -> None:
    rows = [
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A"},
        {"country": "Sri Lanka", "pcode_normalized": "1001", "doctor_name": "Dr B"},
        {"country": "Nepal", "pcode_normalized": "1002", "doctor_name": "Dr C"},
    ]

    assert cross_country_pcode_collisions(rows) == {"1001": ["Nepal", "Sri Lanka"]}


def test_same_country_conflicting_doctor_names_are_reported() -> None:
    rows = [
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A"},
        {"country": "Nepal", "pcode_normalized": "1001", "doctor_name": "Dr A Alias"},
    ]

    assert same_country_doctor_conflicts(rows) == {("Nepal", "1001"): ["Dr A", "Dr A Alias"]}
