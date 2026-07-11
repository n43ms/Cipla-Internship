from decimal import Decimal

from backend.app.services.ai.context_builder import build_compact_context, context_scope
from backend.app.services.ai.query_planner import plan_query


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


def test_context_builder_scopes_budget_query_without_doctor_rows(monkeypatch) -> None:
    from backend.app.services.budget_service import BudgetService
    from backend.app.services.data_quality_service import DataQualityService
    from backend.app.services.doctor_service import DoctorService

    monkeypatch.setattr(
        BudgetService,
        "summary",
        lambda self, **kwargs: {
            "meta": _meta([], ["FX rates are official static company rates."]),
            "plannedBudgetUsd": 100,
            "spendWithoutPlanCount": 2,
            "rows": [{"eventName": "Budget Event", "unspentGapUsd": 10, "currencyCode": "LKR"}],
        },
    )
    monkeypatch.setattr(
        DataQualityService,
        "summary",
        lambda self: {"meta": _meta([], []), "missingFxCount": 0, "fxQuality": []},
    )

    def fail_doctor_call(self, **kwargs):
        raise AssertionError("doctor ROI should not be retrieved for a budget-only query")

    monkeypatch.setattr(DoctorService, "roi", fail_doctor_call)

    context = build_compact_context(
        object(),
        question="Summarize budget variance and FX risk",
        page_context="budget",
        filters={},
        query_plan=plan_query("Summarize budget variance and FX risk", "budget", 40),
    )

    assert "budget" in context
    assert "doctorRoi" not in context
    assert context_scope(context)["sections"] == ["budget", "dataQuality"]


def test_context_builder_fetches_specific_doctor_detail_from_pcode(monkeypatch) -> None:
    from backend.app.repositories.doctor_repository import DoctorRepository
    from backend.app.services.budget_service import BudgetService
    from backend.app.services.data_quality_service import DataQualityService
    from backend.app.services.doctor_service import DoctorService

    monkeypatch.setattr(
        DoctorService,
        "roi",
        lambda self, **kwargs: {
            "meta": _meta([], ["Doctor ROI uses historical RCPA baseline."]),
            "total": 1,
            "darkHorseCount": 1,
            "rows": [
                {
                    "doctorName": "Dr Specific Name",
                    "pcodeNormalized": "12345",
                    "countryName": "Sri Lanka",
                    "totalRoiSpendUsd": 45,
                    "ciplaPrescriptionQty": 100,
                }
            ],
        },
    )
    monkeypatch.setattr(
        BudgetService,
        "summary",
        lambda self, **kwargs: {"meta": _meta([], []), "plannedBudgetUsd": 100, "rows": []},
    )
    monkeypatch.setattr(
        DataQualityService,
        "summary",
        lambda self: {"meta": _meta([], []), "rcpaCoverage": Decimal("0.9")},
    )
    monkeypatch.setattr(
        DoctorRepository,
        "search_doctors",
        lambda self, country, search, limit=5: [
            {
                "country_code": "LK",
                "country_name": "Sri Lanka",
                "pcode_normalized": "12345",
                "doctor_name": "Dr Specific Name",
                "speciality": "Cardiology",
                "doctor_class": "A",
                "engagement_count": 2,
                "total_roi_spend_usd": Decimal("45"),
                "cipla_prescription_qty": Decimal("100"),
                "roi_segment": "dark_horse",
                "quadrant_label": "low effort / high reward",
                "has_rcpa": True,
            }
        ],
    )
    monkeypatch.setattr(
        DoctorRepository,
        "engagement_history",
        lambda self, country_code, pcode: [
            {
                "request_id": "REQ-1",
                "intervention_name": "CME",
                "month": "2026-05",
            }
        ],
    )
    monkeypatch.setattr(
        DoctorRepository,
        "prescription_trend",
        lambda self, country_code, pcode: [{"month": "2026-03", "cipla_prescription_qty": 100}],
    )
    monkeypatch.setattr(
        DoctorRepository,
        "brand_mix",
        lambda self, country_code, pcode: [{"brand_group": "Brand A", "prescription_qty": 80}],
    )
    monkeypatch.setattr(
        DoctorRepository,
        "sponsorship_outcome",
        lambda self, country_code, pcode: {
            "sponsorship_count": 1,
            "paid_engagement_count": 1,
            "no_fee_engagement_count": 0,
            "contracted_amount_usd": Decimal("200"),
            "fmv_amount_usd": Decimal("250"),
            "contract_saving_usd": Decimal("50"),
            "associated_rx_movement_qty": Decimal("20"),
            "evidence_confidence": "medium",
            "evidence_caveats": ["manual_rcpa_mapping_period"],
        },
    )

    context = build_compact_context(
        object(),
        question="Show details for Pcode 12345",
        page_context="doctors",
        filters={"country": "LK"},
        query_plan=plan_query("Show details for Pcode 12345", "doctors", 40),
    )

    details = context["doctorRoi"]["matchedDoctorDetails"]
    assert details[0]["profile"]["doctorName"] == "Dr Specific Name"
    assert details[0]["profile"]["pcodeNormalized"] == "12345"
    assert details[0]["sponsorshipOutcome"]["sponsorship_count"] == 1
    assert details[0]["sponsorshipOutcome"]["associated_rx_movement_qty"] == 20
    assert details[0]["engagementHistory"][0]["request_id"] == "REQ-1"


def test_context_builder_includes_territory_rows_only_when_planned(monkeypatch) -> None:
    from backend.app.services.data_quality_service import DataQualityService
    from backend.app.services.doctor_service import DoctorService
    from backend.app.services.territory_service import TerritoryService

    monkeypatch.setattr(
        TerritoryService,
        "opportunities",
        lambda self, **kwargs: {
            "meta": _meta(["manual_rcpa_mapping"], ["Territory labels are deterministic."]),
            "total": 1,
            "labelCounts": {"underserved": 1},
            "rows": [
                {
                    "countryCode": "LK",
                    "countryName": "Sri Lanka",
                    "territoryName": "Colombo",
                    "patchName": "Patch A",
                    "doctorCount": 3,
                    "engagedDoctorCount": 0,
                    "ciplaPrescriptionQty": 100,
                    "competitorPrescriptionQty": 30,
                    "totalPrescriptionQty": 130,
                    "knownInvestmentUsd": 0,
                    "opportunityLabel": "underserved",
                    "evidenceConfidence": "medium",
                    "sourceCaveats": ["manual_rcpa_mapping_period"],
                }
            ],
        },
    )
    monkeypatch.setattr(
        DoctorService,
        "roi",
        lambda self, **kwargs: {"meta": _meta([], []), "total": 0, "rows": []},
    )
    monkeypatch.setattr(
        DataQualityService,
        "summary",
        lambda self: {"meta": _meta([], []), "validationWarningCount": 0},
    )

    context = build_compact_context(
        object(),
        question="Which territory is underserved?",
        page_context="territory",
        filters={"country": "LK", "opportunityLabel": "underserved"},
        query_plan=plan_query("Which territory is underserved?", "territory", 20),
    )

    assert context["territory"]["topTerritoryRows"][0]["territoryName"] == "Colombo"
    assert context["territory"]["topTerritoryRows"][0]["opportunityLabel"] == "underserved"
    assert "Territory labels are deterministic." in context["limitations"]


def _meta(flags: list[str], limitations: list[str]) -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": {},
        "dataQualityFlags": flags,
        "limitations": limitations,
        "sourceDerivationNotes": [],
    }
