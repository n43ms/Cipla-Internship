from collections.abc import Iterator
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app


class FakeSession:
    pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


def test_budget_doctor_and_data_quality_contracts(monkeypatch) -> None:
    from backend.app.services.budget_service import BudgetService
    from backend.app.services.data_quality_service import DataQualityService
    from backend.app.services.doctor_service import DoctorService

    monkeypatch.setattr(
        BudgetService,
        "summary",
        lambda self, country=None, month=None, include_out_of_scope=False: {
            "meta": _meta(),
            "plannedBudgetUsd": Decimal("1000"),
            "estimatedInterventionLocal": Decimal("310000"),
            "estimatedInterventionUsd": Decimal("1000"),
            "confirmedContractedAmountLocal": Decimal("279000"),
            "confirmedContractedAmountUsd": Decimal("900"),
            "confirmedVsEstimatedVarianceLocal": Decimal("-31000"),
            "confirmedVsEstimatedVarianceUsd": Decimal("-100"),
            "directHcpBtuSpendLocal": Decimal("155000"),
            "directHcpBtuSpendUsd": Decimal("500"),
            "overheadBtcSpendLocal": Decimal("62000"),
            "overheadBtcSpendUsd": Decimal("200"),
            "actualTotalSpendLocal": Decimal("217000"),
            "actualTotalSpendUsd": Decimal("700"),
            "associationAmountLocal": Decimal("0"),
            "unspentGapUsd": Decimal("300"),
            "overrunAmountUsd": Decimal("0"),
            "planWithoutSpendCount": 1,
            "spendWithoutPlanCount": 0,
            "btuBtcReconciliationIssueCount": 0,
            "missingFxCount": 0,
            "provisionalFxCount": 0,
            "currencyCodes": ["LKR"],
            "fxRateStatuses": ["official"],
            "rows": [],
        },
    )
    monkeypatch.setattr(
        DoctorService,
        "roi",
        lambda self, country, segment, quadrant, page, page_size: {
            "meta": _meta(),
            "page": page,
            "pageSize": page_size,
            "total": 1,
            "quadrantCounts": {"low effort / high reward": 1},
            "segmentCounts": {"high_value_unengaged": 1},
            "rows": [
                {
                    "countryCode": "LK",
                    "countryName": "Sri Lanka",
                    "pcodeNormalized": "1001",
                    "doctorName": "Dr Test",
                    "speciality": "Cardiology",
                    "doctorClass": "A",
                    "activeStatus": "Active",
                    "engagementCount": 0,
                    "lastEngagementDate": None,
                    "directHcpBtuSpendUsd": Decimal("0"),
                    "overheadBtcSpendUsd": Decimal("0"),
                    "totalRoiSpendUsd": Decimal("0"),
                    "ciplaPrescriptionQty": Decimal("100"),
                    "competitorPrescriptionQty": Decimal("50"),
                    "totalPrescriptionQty": Decimal("150"),
                    "ciplaShareQty": Decimal("0.6667"),
                    "spendPerCiplaPrescriptionUsd": None,
                    "roiSegment": "high_value_unengaged",
                    "quadrantX": Decimal("0"),
                    "quadrantY": Decimal("100"),
                    "quadrantLabel": "low effort / high reward",
                    "darkHorseFlag": True,
                    "hasRcpa": True,
                    "hasMissingFx": False,
                    "hasProvisionalFx": False,
                }
            ],
        },
    )
    monkeypatch.setattr(
        DataQualityService,
        "summary",
        lambda self: {
            "meta": _meta(),
            "latestIngestion": {
                "id": "run-1",
                "status": "completed",
                "sourceFileCount": 8,
                "totalRowsSeen": 10,
                "totalRowsLoaded": 9,
                "totalRowsSkipped": 1,
                "warningCount": 1,
                "errorCount": 0,
            },
            "sourceFileCount": 8,
            "loadedFileCount": 8,
            "rowsSeen": 10,
            "rowsLoaded": 9,
            "rowsSkipped": 1,
            "validationErrorCount": 0,
            "validationWarningCount": 1,
            "matchCoverage": Decimal("0.8"),
            "pcodeCoverage": Decimal("1"),
            "rcpaCoverage": Decimal("0.9"),
            "missingFxCount": 0,
            "provisionalFxCount": 0,
            "btuBtcReconciliationIssueCount": 0,
            "missingConfirmedAmountCount": 0,
            "spendWithoutPlanCount": 0,
            "planWithoutSpendCount": 1,
            "requestWorkflowCoverage": Decimal("1"),
            "postWorkflowCoverage": Decimal("0.7"),
            "interventionTypeCoverage": Decimal("1"),
            "unmatchedEventCount": 2,
            "derivedSnapshotCount": 1,
            "staleIngestion": False,
            "validationIssues": [],
        },
    )
    monkeypatch.setattr(
        DataQualityService,
        "latest_ingestion",
        lambda self: {
            "id": "run-1",
            "status": "completed",
            "sourceFileCount": 8,
            "totalRowsSeen": 10,
            "totalRowsLoaded": 9,
            "totalRowsSkipped": 1,
            "warningCount": 1,
            "errorCount": 0,
        },
    )
    monkeypatch.setattr(
        DataQualityService,
        "filters",
        lambda self: {
            "countries": [{"value": "LK", "label": "Sri Lanka"}],
            "months": [{"value": "2026-05", "label": "2026-05"}],
            "interventionTypes": [{"value": "CME", "label": "CME"}],
            "specialities": [],
            "doctorClasses": [],
            "roiSegments": [{"value": "high_value_unengaged", "label": "high value unengaged"}],
            "latestIngestionStatus": "completed",
        },
    )

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        assert client.get("/api/budget/summary").json()["confirmedContractedAmountUsd"] == "900"
        assert client.get("/api/doctors/roi?pageSize=5").json()["rows"][0]["darkHorseFlag"] is True
        assert client.get("/api/data-quality").json()["loadedFileCount"] == 8
        assert client.get("/api/filters").json()["latestIngestionStatus"] == "completed"
        assert client.get("/api/ingestion/latest").json()["sourceFileCount"] == 8


def _meta() -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": {},
        "dataQualityFlags": [],
        "limitations": [],
        "sourceDerivationNotes": [],
    }
