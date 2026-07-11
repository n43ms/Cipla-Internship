from collections.abc import Iterator
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app


class FakeSession:
    pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


def test_doctor_roi_contract_forwards_filters_sort_and_returns_segments(monkeypatch) -> None:
    from backend.app.services.doctor_service import DoctorService

    calls: list[dict[str, object]] = []

    def fake_roi(
        self,
        country,
        roi_segment,
        quadrant,
        month_start,
        month_end,
        brand,
        speciality,
        doctor_class,
        include_out_of_scope,
        page,
        page_size,
        sort="darkHorse",
        sort_direction="desc",
    ):
        calls.append(
            {
                "country": country,
                "roi_segment": roi_segment,
                "quadrant": quadrant,
                "month_start": month_start,
                "month_end": month_end,
                "brand": brand,
                "speciality": speciality,
                "doctor_class": doctor_class,
                "include_out_of_scope": include_out_of_scope,
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_direction": sort_direction,
            }
        )
        return {
            "meta": _meta(),
            "page": page,
            "pageSize": page_size,
            "total": 1,
            "sort": sort,
            "sortDirection": sort_direction,
            "darkHorseCount": 1,
            "noRcpaCount": 0,
            "missingFxCount": 0,
            "provisionalFxCount": 0,
            "brandFilterMode": "baseline_inclusion",
            "periodFilterMode": "engagement_period",
            "quadrantCounts": {"low effort / high reward": 1},
            "segmentCounts": {"high_value_unengaged": 1},
            "rows": [_doctor_row()],
        }

    monkeypatch.setattr(DoctorService, "roi", fake_roi)

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        response = client.get(
            "/api/doctors/roi?country=LK&roiSegment=high_value_unengaged&quadrant=low%20effort%20/%20high%20reward&monthStart=2026-04&monthEnd=2026-05&brand=Brand%20A&speciality=Cardiology&doctorClass=A&includeOutOfScope=true&page=2&pageSize=5&sort=ciplaPrescriptionQty&sortDirection=asc"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["darkHorseCount"] == 1
    assert body["rows"][0]["pcodeNormalized"] == "1001"
    assert body["rows"][0]["quadrantLabel"] == "low effort / high reward"
    assert calls[0]["sort"] == "ciplaPrescriptionQty"
    assert calls[0]["sort_direction"] == "asc"
    assert calls[0]["include_out_of_scope"] is True


def test_doctor_detail_contract_returns_profile_history_trend_and_brand_mix(monkeypatch) -> None:
    from backend.app.services.doctor_service import DoctorService

    monkeypatch.setattr(
        DoctorService,
        "detail",
        lambda self, country_code, pcode: {
            "meta": _meta({"countryCode": country_code, "pcode": pcode}),
            "profile": _doctor_row(),
            "sponsorshipOutcome": {
                "sponsorshipCount": 1,
                "paidEngagementCount": 1,
                "noFeeEngagementCount": 0,
                "paidServiceCount": 0,
                "contractedAmountUsd": Decimal("100"),
                "fmvAmountUsd": Decimal("120"),
                "contractSavingUsd": Decimal("20"),
                "doctorAttributableExpenseLocal": Decimal("0"),
                "knownEngagementInvestmentUsd": Decimal("100"),
                "preWindowCiplaRxQty": Decimal("50"),
                "postWindowCiplaRxQty": Decimal("70"),
                "associatedRxMovementQty": Decimal("20"),
                "preWindowMonthCount": 3,
                "postWindowMonthCount": 3,
                "evidenceConfidence": "high",
                "evidenceCaveats": [],
            },
            "engagementHistory": [
                {
                    "requestId": "REQ-1",
                    "interventionName": "Diabetes CME",
                    "interventionType": "CME",
                    "month": "2026-05",
                    "actualInterventionDate": "2026-05-10",
                    "totalRoiSpendUsd": Decimal("10"),
                    "fxRateStatus": "official",
                }
            ],
            "prescriptionTrend": [
                {
                    "month": "2026-05",
                    "ciplaPrescriptionQty": Decimal("100"),
                    "competitorPrescriptionQty": Decimal("50"),
                    "totalPrescriptionQty": Decimal("150"),
                }
            ],
            "brandMix": [
                {
                    "brandGroup": "Brand A",
                    "ownOrCompetitor": "own",
                    "prescriptionQty": Decimal("100"),
                    "prescriptionValueLocal": Decimal("2500"),
                }
            ],
        },
    )

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        response = client.get("/api/doctors/LK/1001")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["doctorName"] == "Dr Test"
    assert body["sponsorshipOutcome"]["sponsorshipCount"] == 1
    assert body["sponsorshipOutcome"]["associatedRxMovementQty"] == 20.0
    assert body["engagementHistory"][0]["requestId"] == "REQ-1"
    assert body["prescriptionTrend"][0]["ciplaPrescriptionQty"] == 100.0
    assert body["brandMix"][0]["brandGroup"] == "Brand A"


def _doctor_row() -> dict[str, object]:
    return {
        "countryCode": "LK",
        "countryName": "Sri Lanka",
        "pcodeNormalized": "1001",
        "doctorName": "Dr Test",
        "speciality": "Cardiology",
        "doctorClass": "A",
        "activeStatus": "Active",
        "engagementCount": 0,
        "firstEngagementDate": None,
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
        "darkHorseUnengagedFlag": True,
        "highValueEngagedFlag": False,
        "hasRcpa": True,
        "hasMissingFx": False,
        "hasProvisionalFx": False,
        "rcpaFirstMonth": "2025-04-01",
        "rcpaLastMonth": "2026-03-01",
        "rcpaMonthCount": 12,
    }


def _meta(filters: dict[str, object] | None = None) -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": filters or {},
        "dataQualityFlags": [],
        "limitations": [],
        "sourceDerivationNotes": [],
    }
