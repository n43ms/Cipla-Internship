import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { BudgetUtilization } from "../src/pages/BudgetUtilization";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("Budget utilization page", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders budget cards, FX warning, BTU/BTC split, and event gaps", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/filters")) return ok(filters());
      if (url.includes("/api/budget/summary")) return ok(budgetSummary());
      return ok({});
    });

    renderWithProviders(<BudgetUtilization />);

    await waitFor(() => expect(screen.getByText("Budget utilization")).toBeInTheDocument());
    expect(screen.getByText("Confirmed contracted")).toBeInTheDocument();
    expect(screen.getByText("Budget split")).toBeInTheDocument();
    expect(screen.getByText("Local currency totals")).toBeInTheDocument();
    expect(screen.getByText("Budget quality notes")).toBeInTheDocument();
    expect(screen.queryByText("1 rows use provisional FX.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /budget quality notes/i }));
    expect(screen.getByText("1 rows use provisional FX.")).toBeInTheDocument();
    expect(screen.getByText("Diabetes CME")).toBeInTheDocument();
    expect(screen.getByText("Event budget gaps and unmatched spend")).toBeInTheDocument();
  });
});

function filters() {
  return {
    countries: [{ value: "LK", label: "Sri Lanka" }],
    months: [{ value: "2026-05", label: "2026-05" }],
    interventionTypes: [],
    brands: [],
    specialities: [],
    doctorClasses: [],
    roiSegments: [],
    latestIngestionStatus: "completed_with_warnings",
  };
}

function budgetSummary() {
  return {
    meta: {
      generatedAt: "2026-06-19T00:00:00Z",
      latestIngestionStatus: "completed_with_warnings",
      filtersApplied: {},
      dataQualityFlags: ["provisional_fx"],
      limitations: ["Some amounts use provisional FX."],
      sourceDerivationNotes: [],
    },
    plannedBudgetUsd: 1000,
    estimatedInterventionLocal: 310000,
    estimatedInterventionUsd: 1000,
    confirmedContractedAmountLocal: 279000,
    confirmedContractedAmountUsd: 900,
    confirmedVsEstimatedVarianceLocal: -31000,
    confirmedVsEstimatedVarianceUsd: -100,
    directHcpBtuSpendLocal: 155000,
    directHcpBtuSpendUsd: 500,
    overheadBtcSpendLocal: 62000,
    overheadBtcSpendUsd: 200,
    actualTotalSpendLocal: 217000,
    actualTotalSpendUsd: 700,
    associationAmountLocal: 0,
    unspentGapUsd: 300,
    overrunAmountUsd: 0,
    planWithoutSpendCount: 1,
    spendWithoutPlanCount: 0,
    btuBtcReconciliationIssueCount: 0,
    missingFxCount: 0,
    provisionalFxCount: 1,
    currencyCodes: ["LKR"],
    fxRateStatuses: ["official", "provisional"],
    localTotalsByCurrency: [
      {
        currencyCode: "LKR",
        estimatedInterventionLocal: 310000,
        confirmedContractedAmountLocal: 279000,
        directHcpBtuSpendLocal: 155000,
        overheadBtcSpendLocal: 62000,
        actualTotalSpendLocal: 217000,
        associationAmountLocal: 0,
        rowCount: 1,
        missingFxCount: 0,
        provisionalFxCount: 0,
      },
    ],
    page: 1,
    pageSize: 25,
    total: 1,
    sort: "unspentGapUsd",
    sortDirection: "desc",
    rows: [
      {
        eventName: "Diabetes CME",
        eventType: "CME",
        country: "Sri Lanka",
        month: "2026-05",
        matchStatus: "matched",
        plannedBudgetUsd: 1000,
        estimatedInterventionLocal: 310000,
        confirmedContractedAmountLocal: 279000,
        actualTotalExpenseLocal: 217000,
        directHcpBtuSpendLocal: 155000,
        overheadBtcSpendLocal: 62000,
        actualTotalExpenseUsd: 700,
        unspentGapUsd: 300,
        overrunAmountUsd: 0,
        currencyCode: "LKR",
        fxRateStatus: "official",
        btuBtcReconciliationStatus: "reconciled",
        spendWithoutPlan: false,
        planWithoutSpend: false,
        rowKind: "matched_request_evidence",
      },
    ],
  };
}
