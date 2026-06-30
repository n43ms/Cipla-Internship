from collections.abc import Iterator
from decimal import Decimal

from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app


class FakeSession:
    pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


def test_budget_summary_contract_includes_financial_split_fx_and_sort(monkeypatch) -> None:
    from backend.app.services.budget_service import BudgetService

    calls: list[dict[str, object]] = []

    def fake_summary(
        self,
        country=None,
        month=None,
        include_out_of_scope=False,
        page=1,
        page_size=100,
        sort="priority",
        sort_direction="desc",
    ):
        calls.append(
            {
                "country": country,
                "month": month,
                "include_out_of_scope": include_out_of_scope,
                "page": page,
                "page_size": page_size,
                "sort": sort,
                "sort_direction": sort_direction,
            }
        )
        return {
            "meta": _meta({"country": country, "month": month, "sort": sort, "sortDirection": sort_direction}),
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
            "provisionalFxCount": 1,
            "currencyCodes": ["LKR", "NPR"],
            "fxRateStatuses": ["official", "provisional"],
            "localTotalsByCurrency": [],
            "page": page,
            "pageSize": page_size,
            "total": 1,
            "sort": sort,
            "sortDirection": sort_direction,
            "rows": [
                {
                    "eventName": "Diabetes CME",
                    "eventType": "CME",
                    "country": "Sri Lanka",
                    "month": "2026-05",
                    "matchStatus": "matched",
                    "plannedBudgetUsd": Decimal("1000"),
                    "actualTotalExpenseUsd": Decimal("700"),
                    "unspentGapUsd": Decimal("300"),
                    "fxRateStatus": "official",
                    "btuBtcReconciliationStatus": "reconciled",
                    "spendWithoutPlan": False,
                    "planWithoutSpend": False,
                    "rowKind": "matched_request_evidence",
                }
            ],
        }

    monkeypatch.setattr(BudgetService, "summary", fake_summary)

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    with TestClient(app) as client:
        response = client.get(
            "/api/budget/summary?country=LK&month=2026-05&page=2&pageSize=5&sort=unspentGapUsd&sortDirection=asc&includeOutOfScope=true"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["confirmedContractedAmountUsd"] == 900.0
    assert body["actualTotalSpendUsd"] == 700.0
    assert body["directHcpBtuSpendUsd"] == 500.0
    assert body["overheadBtcSpendUsd"] == 200.0
    assert body["fxRateStatuses"] == ["official", "provisional"]
    assert body["rows"][0]["btuBtcReconciliationStatus"] == "reconciled"
    assert calls == [
        {
            "country": "LK",
            "month": "2026-05",
            "include_out_of_scope": True,
            "page": 2,
            "page_size": 5,
            "sort": "unspentGapUsd",
            "sort_direction": "asc",
        }
    ]


def _meta(filters: dict[str, object] | None = None) -> dict:
    return {
        "generatedAt": "2026-06-19T00:00:00Z",
        "latestIngestionStatus": "completed",
        "filtersApplied": filters or {},
        "dataQualityFlags": [],
        "limitations": [],
        "sourceDerivationNotes": [],
    }
