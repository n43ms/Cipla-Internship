from collections.abc import Iterator
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app


class FakeSession:
    pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


def test_data_quality_filters_and_latest_ingestion_contract(monkeypatch) -> None:
    from backend.app.services.data_quality_service import DataQualityService

    monkeypatch.setattr(DataQualityService, "summary", lambda self: _summary())
    monkeypatch.setattr(DataQualityService, "latest_ingestion", lambda self: _latest_ingestion())
    monkeypatch.setattr(
        DataQualityService,
        "filters",
        lambda self: {
            "countries": [{"value": "LK", "label": "Sri Lanka"}],
            "months": [{"value": "2026-05", "label": "2026-05"}],
            "interventionTypes": [{"value": "CME", "label": "CME"}],
            "brands": [{"value": "Brand A", "label": "Brand A"}],
            "specialities": [{"value": "Cardiology", "label": "Cardiology"}],
            "doctorClasses": [{"value": "A", "label": "A"}],
            "roiSegments": [{"value": "high_value_unengaged", "label": "high value unengaged"}],
            "latestIngestionStatus": "completed_with_warnings",
        },
    )

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        quality = client.get("/api/data-quality").json()
        filters = client.get("/api/filters").json()
        latest = client.get("/api/ingestion/latest").json()

    assert quality["loadedFileCount"] == 8
    assert quality["matchCoverage"] == 0.6138
    assert quality["rcpaCoveredMonthEnd"] == "2026-07-01"
    assert quality["rcpaManualMappingCount"] == 42
    assert quality["validationIssues"][0]["errorCode"] == "missing_field"
    assert quality["fxQuality"][0]["rateStatus"] == "official"
    assert filters["latestIngestionStatus"] == "completed_with_warnings"
    assert filters["brands"][0]["value"] == "Brand A"
    assert latest["status"] == "completed_with_warnings"
    assert latest["sourceFileCount"] == 8


def _summary() -> dict:
    return {
        "meta": _meta(),
        "latestIngestion": _latest_ingestion(),
        "sourceFileCount": 8,
        "loadedFileCount": 8,
        "rowsSeen": 1179273,
        "rowsLoaded": 423654,
        "rowsSkipped": 42,
        "validationErrorCount": 0,
        "validationWarningCount": 3,
        "matchCoverage": Decimal("0.6138"),
        "pcodeCoverage": Decimal("1"),
        "rcpaCoverage": Decimal("0.9926"),
        "rcpaManualMappingCount": 42,
        "rcpaSystemMappingCount": 120,
        "rcpaSourceMappingCount": 8,
        "rcpaUnknownMappingCount": 0,
        "rcpaCoveredMonthStart": "2024-04-01",
        "rcpaCoveredMonthEnd": "2026-07-01",
        "missingFxCount": 0,
        "provisionalFxCount": 1555,
        "btuBtcReconciliationIssueCount": 0,
        "missingConfirmedAmountCount": 0,
        "spendWithoutPlanCount": 0,
        "planWithoutSpendCount": 1,
        "requestWorkflowCoverage": Decimal("1"),
        "postWorkflowCoverage": Decimal("0.7"),
        "interventionTypeCoverage": Decimal("1"),
        "unmatchedEventCount": 158,
        "derivedSnapshotCount": 31,
        "serialMonthParseCount": 0,
        "staticFxSeedDate": "2026-06-16",
        "officialLkrRateToUsd": Decimal("0.0032258065"),
        "actualAttendanceMissingPcodeCount": 0,
        "unallocatedDoctorSpendLocal": Decimal("0"),
        "unallocatedDoctorSpendUsd": Decimal("0"),
        "staleIngestion": False,
        "validationIssues": [
            {
                "severity": "warning",
                "sourceFile": "planner.xlsx",
                "sheetName": "YP FY27",
                "rowNumber": 10,
                "entityType": "plan_event",
                "fieldName": "country",
                "errorCode": "missing_field",
                "message": "Missing optional country field",
            }
        ],
        "sourceFiles": [
            {
                "sourceFile": "planner.xlsx",
                "sourceType": "planner",
                "status": "completed_with_warnings",
                "rowsSeen": 10,
                "rowsLoaded": 9,
                "rowsSkipped": 1,
                "warningCount": 1,
                "errorCount": 0,
                "periodStart": None,
                "periodEnd": None,
            }
        ],
        "unmatchedBySource": [{"sourceType": "planner", "reasonCode": "planner_only", "recordCount": 2}],
        "unmatchedRecords": [
            {
                "sourceType": "planner",
                "country": "Sri Lanka",
                "month": "2026-05",
                "eventName": "Unmatched CME",
                "eventType": "CME",
                "reasonCode": "planner_only",
                "reasonDetail": "No request found",
                "candidateMatch": None,
                "confidence": Decimal("0"),
            }
        ],
        "fxQuality": [
            {
                "currencyCode": "LKR",
                "rateStatus": "official",
                "rateToUsd": Decimal("0.0032258065"),
                "rateDate": "2026-06-16",
                "source": "company",
                "rowCount": 1,
            }
        ],
    }


def _latest_ingestion() -> dict:
    return {
        "id": "run-1",
        "status": "completed_with_warnings",
        "startedAt": None,
        "completedAt": None,
        "sourceFileCount": 8,
        "totalRowsSeen": 1179273,
        "totalRowsLoaded": 423654,
        "totalRowsSkipped": 42,
        "warningCount": 3,
        "errorCount": 0,
    }


def _meta() -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed_with_warnings",
        "filtersApplied": {},
        "dataQualityFlags": ["provisional_fx"],
        "limitations": ["Some rows use provisional FX."],
        "sourceDerivationNotes": [],
    }
