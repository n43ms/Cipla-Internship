from ingestion.normalizers.intervention_reconciliation import reconcile_doctor_interventions


def test_reconciles_doctor_rows_to_consolidated_request_id_first() -> None:
    doctor_records = [
        {
            "country": "Sri Lanka",
            "month_start_date": "2026-07-01",
            "intervention_id": "REQ-SP-1",
            "intervention_name_normalized": "international congress",
        }
    ]
    request_records = [
        {
            "country": "Sri Lanka",
            "month_start_date": "2026-07-01",
            "request_uid": "REQ-SP-1",
            "intervention_name_normalized": "international congress",
        }
    ]

    matches = reconcile_doctor_interventions(doctor_records, request_records)

    assert matches[0].match_method == "intervention_id"
    assert matches[0].confidence == 1.0
    assert matches[0].request_record == request_records[0]


def test_reconciliation_keeps_unmatched_doctor_rows_explicit() -> None:
    matches = reconcile_doctor_interventions(
        [{"country": "Nepal", "month_start_date": "2026-07-01", "intervention_id": "REQ-X"}],
        [],
    )

    assert matches[0].match_method == "unmatched"
    assert matches[0].request_record is None
    assert matches[0].confidence == 0.0
