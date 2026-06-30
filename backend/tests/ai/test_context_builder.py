from decimal import Decimal

from backend.app.services.ai.context_builder import build_compact_context, context_scope


def test_context_builder_uses_service_outputs_with_specific_bounded_rows(monkeypatch) -> None:
    from backend.app.services.budget_service import BudgetService
    from backend.app.services.data_quality_service import DataQualityService
    from backend.app.services.doctor_service import DoctorService
    from backend.app.services.execution_service import ExecutionService
    from backend.app.services.intervention_service import InterventionService
    from backend.app.services.workflow_service import WorkflowService

    monkeypatch.setattr(
        ExecutionService,
        "summary",
        lambda self, country=None, month=None, include_out_of_scope=False: {
            "meta": _meta(["weak_match_coverage"], ["Execution limitation."]),
            "plannedEvents": 10,
            "matchedEvents": 6,
            "weakOrUnmatchedEvents": 4,
            "matchCoverage": Decimal("0.6"),
        },
    )
    monkeypatch.setattr(
        ExecutionService,
        "events",
        lambda self, **kwargs: {
            "meta": _meta([], []),
            "total": 12,
            "rows": [
                {
                    "eventName": f"Event {index}",
                    "country": "Sri Lanka",
                    "month": "2026-05",
                    "matchStatus": "matched",
                    "sourceReferences": {"planEventId": f"plan-{index}"},
                }
                for index in range(10)
            ],
        },
    )
    monkeypatch.setattr(
        WorkflowService,
        "summary",
        lambda self, country=None, month=None, intervention_type=None, include_out_of_scope=False: {
            "meta": _meta([], []),
            "pendingReportCount": 2,
        },
    )
    monkeypatch.setattr(
        WorkflowService,
        "requests",
        lambda self, **kwargs: {
            "meta": _meta([], []),
            "total": 8,
            "rows": [
                {"reqId": f"REQ-{index}", "repName": "Rep Name", "interventionType": "CME"}
                for index in range(8)
            ],
        },
    )
    monkeypatch.setattr(
        InterventionService,
        "mix",
        lambda self, country=None, month=None, include_out_of_scope=False: {
            "meta": _meta([], []),
            "rows": [
                {"interventionType": f"Type {index}", "requestCount": index}
                for index in range(10)
            ],
        },
    )
    monkeypatch.setattr(
        BudgetService,
        "summary",
        lambda self, **kwargs: {
            "meta": _meta([], []),
            "plannedBudgetUsd": 100,
            "rows": [
                {
                    "eventName": f"Event {index}",
                    "unspentGapUsd": index,
                    "currencyCode": "LKR",
                    "actualTotalExpenseLocal": 31000,
                }
                for index in range(10)
            ],
        },
    )
    monkeypatch.setattr(
        DoctorService,
        "roi",
        lambda self, **kwargs: {
            "meta": _meta([], []),
            "darkHorseCount": 1,
            "rows": [
                {
                    "doctorName": "Dr Specific Name",
                    "pcodeNormalized": "12345",
                    "ciplaPrescriptionQty": 100,
                    "quadrantLabel": "low effort / high reward",
                    "totalRoiSpendUsd": 45,
                }
            ],
        },
    )
    monkeypatch.setattr(
        DataQualityService,
        "summary",
        lambda self: {
            "meta": _meta([], []),
            "loadedFileCount": 8,
            "validationWarningCount": 1,
            "unmatchedBySource": [
                {"sourceType": "planner", "reasonCode": "no_request", "recordCount": 4}
            ],
            "fxQuality": [{"currencyCode": "LKR", "rateStatus": "official", "rateToUsd": 0.0032}],
        },
    )

    context = build_compact_context(
        object(),
        question="execution risk",
        page_context="execution",
        filters={"country": "LK", "month": "2026-05", "irrelevant": "drop"},
        max_chars=12000,
        row_limit=7,
    )

    assert context["filters"] == {"country": "LK", "month": "2026-05"}
    assert context["execution"]["weakOrUnmatchedEvents"] == 4
    assert len(context["interventions"]["topRows"]) == 7
    assert len(context["execution"]["eventRows"]) == 7
    assert len(context["workflow"]["requestRows"]) == 7
    assert context["doctorRoi"]["topDoctorOpportunityRows"][0]["doctorName"] == "Dr Specific Name"
    assert context["doctorRoi"]["topDoctorOpportunityRows"][0]["pcodeNormalized"] == "12345"
    assert context["budget"]["topGapRows"][0]["currencyCode"] == "LKR"
    assert context["contextPolicy"]["specificNamesAmountsPcodesAndCurrenciesIncluded"] is True
    assert "Execution limitation." in context["limitations"]
    assert context_scope(context)["sections"] == [
        "execution",
        "workflow",
        "interventions",
        "budget",
        "doctorRoi",
        "dataQuality",
    ]


def _meta(flags: list[str], limitations: list[str]) -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": {},
        "dataQualityFlags": flags,
        "limitations": limitations,
        "sourceDerivationNotes": [],
    }
