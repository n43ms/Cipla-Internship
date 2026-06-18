from datetime import date

from ingestion.reconciliation.sri_lanka_may_derivation import derive_sri_lanka_may_snapshots


def test_sri_lanka_may_requests_derive_labeled_execution_snapshot_rows() -> None:
    rows = derive_sri_lanka_may_snapshots(
        [
            {
                "country": "Sri Lanka",
                "month_start_date": date(2026, 5, 1),
                "intervention_name": "Diabetes CME",
                "intervention_type": "CME",
                "intervention_sub_type": "Local",
                "attended_customer_count": 5,
                "expected_customer_count": 8,
                "request_approval_status": "approved",
            },
            {
                "country": "Nepal",
                "month_start_date": date(2026, 5, 1),
                "intervention_name": "Ignored",
            },
        ]
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["country"] == "Sri Lanka"
    assert row["snapshot_source"] == "derived_from_consolidation"
    assert row["normalized_status"] == "executed"
    assert row["engaged_hcps"] == 5
    assert row["raised_request_count"] == 1
