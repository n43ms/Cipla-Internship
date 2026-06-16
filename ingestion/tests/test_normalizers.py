from ingestion.normalizers import (
    currency_for_country,
    normalize_event_name,
    normalize_execution_status,
    normalize_workflow_status,
)


def test_event_status_workflow_and_currency_normalizers() -> None:
    assert normalize_event_name("Diabetes CME - Apr") == "diabetes cme"
    assert normalize_execution_status("Executed") == "executed"
    assert normalize_execution_status("1") == "executed"
    assert normalize_execution_status("", raised_request_count=0) == "action_due"
    assert normalize_workflow_status("Sent for Correction") == "sent_for_correction"
    assert currency_for_country("Sri Lanka") == "LKR"

