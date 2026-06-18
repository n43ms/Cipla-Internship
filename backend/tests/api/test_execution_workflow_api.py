from collections.abc import Iterator
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app


class FakeSession:
    pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


def test_execution_workflow_and_intervention_contracts(monkeypatch) -> None:
    from backend.app.services.execution_service import ExecutionService
    from backend.app.services.intervention_service import InterventionService
    from backend.app.services.workflow_service import WorkflowService

    monkeypatch.setattr(
        ExecutionService,
        "summary",
        lambda self, country=None, month=None, include_out_of_scope=False: {
            "meta": _meta(),
            "plannedEvents": 2,
            "matchedEvents": 1,
            "weakOrUnmatchedEvents": 1,
            "executedEvents": 1,
            "actionDueEvents": 1,
            "plannedEventsWithExecutedEvidence": 1,
            "plannedEventsWithActionDueEvidence": 1,
            "executedSnapshotCount": 2,
            "actionDueSnapshotCount": 1,
            "plannedHcps": 10,
            "engagedHcps": 5,
            "matchedEngagedHcps": 5,
            "rawEngagedHcps": 8,
            "hcpExecutionRate": Decimal("0.5"),
            "eventExecutionRate": Decimal("0.5"),
            "matchCoverage": Decimal("0.5"),
            "snapshotSourceCounts": {"derived_from_consolidation": 1},
            "primaryScope": True,
            "scopeStatuses": ["primary_phase4_scope"],
            "scopeReasons": ["Primary Phase 4 scope."],
        },
    )
    monkeypatch.setattr(
        ExecutionService,
        "events",
        lambda self, country, month, page, page_size, include_out_of_scope=False: {
            "meta": _meta(),
            "page": page,
            "pageSize": page_size,
            "total": 1,
            "rows": [
                {
                    "sourceType": "planner",
                    "eventName": "Diabetes CME",
                    "eventType": "CME",
                    "country": "Sri Lanka",
                    "month": "May 2026",
                    "matchStatus": "weak_match",
                    "confidence": Decimal("0.75"),
                    "candidateMatch": "Diabetes CME May",
                    "unmatchedReasonCode": "name_mismatch",
                    "unmatchedReasonDetail": "The event name matched only weakly.",
                    "isPrimaryPhase4Scope": True,
                    "scopeStatus": "primary_phase4_scope",
                    "scopeReason": "Primary Phase 4 scope.",
                    "matchGrain": "single_match",
                    "sourceReferences": {},
                }
            ],
        },
    )
    monkeypatch.setattr(
        ExecutionService,
        "filter_options",
        lambda self: {
            "countries": [{"value": "LK", "label": "Sri Lanka"}],
            "months": [{"value": "2026-05", "label": "2026-05"}],
            "recommendedMonth": {"value": "2026-05", "label": "2026-05"},
        },
    )
    monkeypatch.setattr(
        WorkflowService,
        "summary",
        lambda self, country=None, month=None, intervention_type=None, include_out_of_scope=False: {
            "meta": _meta(),
            "requestApprovalCounts": {"approved": 1},
            "requestConfirmationCounts": {"confirmed": 1},
            "postApprovalCounts": {"pending_owner": 1},
            "postConfirmationCounts": {"draft": 1},
            "ownerStageCounts": {"manager": 1},
            "pendingRequestCount": 0,
            "pendingReportCount": 1,
            "reportsSentForCorrection": 0,
            "reportsApproved": 0,
            "expenseSubmittedCoverage": 1,
            "expenseConfirmedCoverage": 0,
            "primaryScope": True,
            "scopeStatuses": ["primary_phase4_scope"],
            "scopeReasons": ["Primary Phase 4 scope."],
        },
    )
    monkeypatch.setattr(
        WorkflowService,
        "requests",
        lambda self, country, month, intervention_type, workflow_status, page, page_size, include_out_of_scope=False: {
            "meta": _meta(),
            "page": page,
            "pageSize": page_size,
            "total": 0,
            "rows": [],
        },
    )
    monkeypatch.setattr(
        InterventionService,
        "mix",
        lambda self, country=None, month=None, include_out_of_scope=False: {
            "meta": _meta(),
            "rows": [
                {
                    "interventionType": "CME",
                    "interventionSubType": "Local",
                    "requestCount": 1,
                    "executedCount": 1,
                    "executedRequestCount": 1,
                    "matchedRequestCount": 1,
                    "executedSnapshotCount": 1,
                    "actionDueCount": 0,
                    "actionDueRequestCount": 0,
                    "actionDueSnapshotCount": 0,
                    "matchedWithoutExecutionCount": 0,
                    "approvedCount": 1,
                    "reportPendingCount": 0,
                    "confirmedContractedAmount": Decimal("1000"),
                    "directHcpBtuSpend": Decimal("600"),
                    "overheadBtcSpend": Decimal("200"),
                    "totalActualSpend": Decimal("800"),
                    "fxRateStatus": "official",
                }
            ],
        },
    )

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        assert client.get("/api/execution/summary").json()["plannedEvents"] == 2
        filter_response = client.get("/api/execution/filter-options")
        assert filter_response.json()["recommendedMonth"]["value"] == "2026-05"
        event_response = client.get("/api/execution/events?page=2&pageSize=10")
        assert event_response.json()["page"] == 2
        assert event_response.json()["pageSize"] == 10
        assert event_response.json()["rows"][0]["matchStatus"] == "weak_match"
        assert client.get("/api/workflow/summary").json()["pendingReportCount"] == 1
        workflow_response = client.get(
            "/api/workflow/requests?interventionType=CME&workflowStatus=approved&pageSize=5"
        )
        assert workflow_response.json()["pageSize"] == 5
        assert workflow_response.json()["rows"] == []
        assert client.get("/api/interventions/mix").json()["rows"][0]["interventionType"] == "CME"


def test_phase4_openapi_uses_camel_case_query_contract() -> None:
    app = create_app()
    app.dependency_overrides[get_session] = fake_session

    schema = app.openapi()
    execution_params = {
        parameter["name"]
        for parameter in schema["paths"]["/api/execution/events"]["get"]["parameters"]
    }
    workflow_params = {
        parameter["name"]
        for parameter in schema["paths"]["/api/workflow/requests"]["get"]["parameters"]
    }

    assert "pageSize" in execution_params
    assert "includeOutOfScope" in execution_params
    assert "page_size" not in execution_params
    intervention_params = {
        parameter["name"]
        for parameter in schema["paths"]["/api/interventions/mix"]["get"]["parameters"]
    }
    assert "includeOutOfScope" in intervention_params
    assert {"interventionType", "workflowStatus", "pageSize"}.issubset(workflow_params)
    assert "includeOutOfScope" in workflow_params
    assert "workflow_status" not in workflow_params


def _meta() -> dict:
    return {
        "generatedAt": "2026-06-17T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": {},
        "dataQualityFlags": [],
        "limitations": [],
        "sourceDerivationNotes": [],
    }
