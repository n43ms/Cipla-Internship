from ingestion.normalizers.workflow_status import normalize_workflow_status


def test_workflow_governance_status_mapping() -> None:
    assert normalize_workflow_status("Request Submitted Pending With Manager") == "pending_owner"
    assert normalize_workflow_status("Report in Approval Pending With Finance") == "pending_owner"
    assert normalize_workflow_status("Pending for confirmation") == "pending_confirmation"
    assert normalize_workflow_status("Sent for Correction") == "sent_for_correction"
    assert normalize_workflow_status("Deleted") == "deleted"
    assert normalize_workflow_status("Draft") == "draft"
    assert normalize_workflow_status("Approved") == "approved"
