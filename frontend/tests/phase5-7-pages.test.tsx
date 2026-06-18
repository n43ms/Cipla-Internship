import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("Phase 5-7 dashboard pages", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders budget utilization, doctor ROI, and data quality from backend APIs", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/data-quality")) return ok(dataQuality());
      if (url.includes("/api/budget/summary")) return ok(budgetSummary());
      if (url.includes("/api/doctors/roi")) return ok(doctorRoi());
      if (url.includes("/api/doctors/LK/1001")) return ok(doctorDetail());
      if (url.includes("/api/execution/filter-options")) {
        return ok({ countries: [], months: [], recommendedMonth: null });
      }
      if (url.includes("/api/execution/summary")) return ok(executionSummary());
      if (url.includes("/api/execution/events")) {
        return ok({ meta: meta(), page: 1, pageSize: 25, total: 0, rows: [] });
      }
      if (url.includes("/api/workflow/summary")) return ok(workflowSummary());
      if (url.includes("/api/workflow/requests")) {
        return ok({ meta: meta(), page: 1, pageSize: 8, total: 0, rows: [] });
      }
      if (url.includes("/api/interventions/mix")) return ok({ meta: meta(), rows: [] });
      return ok({});
    });

    renderWithProviders(<App />);

    await waitFor(() => expect(screen.getByText("Planned vs actual execution")).toBeInTheDocument());

    fireEvent.click(screen.getByText("Budget"));
    await waitFor(() => expect(screen.getByText("Budget utilization")).toBeInTheDocument());
    expect(screen.getByText("Confirmed contracted")).toBeInTheDocument();
    expect(screen.getByText("Budget split")).toBeInTheDocument();
    expect(screen.getByText("Diabetes CME")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Doctor ROI"));
    await waitFor(() => expect(screen.getByText("Doctor opportunities and missed value")).toBeInTheDocument());
    expect(screen.getByText("ROI quadrant matrix")).toBeInTheDocument();
    expect(screen.getByText("Dr Test")).toBeInTheDocument();
    fireEvent.click(screen.getByText("Open"));
    await waitFor(() => expect(screen.getByText("Engagement history")).toBeInTheDocument());

    fireEvent.click(screen.getByText("Data Quality"));
    await waitFor(() => expect(screen.getByText("Data quality")).toBeInTheDocument());
    expect(screen.getByText("Loaded files")).toBeInTheDocument();
    expect(screen.getByText("Validation drilldown")).toBeInTheDocument();
    expect(screen.getByText("missing_field")).toBeInTheDocument();
  });
});

function meta() {
  return {
    generatedAt: "2026-06-19T00:00:00Z",
    latestIngestionStatus: "completed",
    filtersApplied: {},
    dataQualityFlags: [],
    limitations: [],
    sourceDerivationNotes: [],
  };
}

function dataQuality() {
  return {
    meta: meta(),
    latestIngestion: { id: "run-1", status: "completed", startedAt: null, completedAt: null, sourceFileCount: 8, totalRowsSeen: 10, totalRowsLoaded: 9, totalRowsSkipped: 1, warningCount: 1, errorCount: 0 },
    sourceFileCount: 8,
    loadedFileCount: 8,
    rowsSeen: 10,
    rowsLoaded: 9,
    rowsSkipped: 1,
    validationErrorCount: 0,
    validationWarningCount: 1,
    matchCoverage: 0.8,
    pcodeCoverage: 1,
    rcpaCoverage: 0.9,
    missingFxCount: 0,
    provisionalFxCount: 0,
    btuBtcReconciliationIssueCount: 0,
    missingConfirmedAmountCount: 0,
    spendWithoutPlanCount: 0,
    planWithoutSpendCount: 1,
    requestWorkflowCoverage: 1,
    postWorkflowCoverage: 0.7,
    interventionTypeCoverage: 1,
    unmatchedEventCount: 2,
    derivedSnapshotCount: 1,
    staleIngestion: false,
    validationIssues: [{ severity: "warning", sourceFile: "test.xlsx", sheetName: "Working", rowNumber: 2, entityType: "request", fieldName: "country", errorCode: "missing_field", message: "Missing country" }],
  };
}

function budgetSummary() {
  return {
    meta: meta(),
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
    provisionalFxCount: 0,
    currencyCodes: ["LKR"],
    fxRateStatuses: ["official"],
    rows: [{ eventName: "Diabetes CME", eventType: "CME", country: "Sri Lanka", month: "2026-05", matchStatus: "matched", plannedBudgetUsd: 1000, actualTotalExpenseUsd: 700, unspentGapUsd: 300, fxRateStatus: "official", btuBtcReconciliationStatus: "reconciled", spendWithoutPlan: false, planWithoutSpend: false }],
  };
}

function doctorRoi() {
  return {
    meta: meta(),
    page: 1,
    pageSize: 50,
    total: 1,
    quadrantCounts: { "low effort / high reward": 1 },
    segmentCounts: { high_value_unengaged: 1 },
    rows: [{
      countryCode: "LK",
      countryName: "Sri Lanka",
      pcodeNormalized: "1001",
      doctorName: "Dr Test",
      speciality: "Cardiology",
      doctorClass: "A",
      activeStatus: "Active",
      engagementCount: 0,
      lastEngagementDate: null,
      directHcpBtuSpendUsd: 0,
      overheadBtcSpendUsd: 0,
      totalRoiSpendUsd: 0,
      ciplaPrescriptionQty: 100,
      competitorPrescriptionQty: 50,
      totalPrescriptionQty: 150,
      ciplaShareQty: 0.66,
      spendPerCiplaPrescriptionUsd: null,
      roiSegment: "high_value_unengaged",
      quadrantX: 0,
      quadrantY: 100,
      quadrantLabel: "low effort / high reward",
      darkHorseFlag: true,
      hasRcpa: true,
      hasMissingFx: false,
      hasProvisionalFx: false,
    }],
  };
}

function doctorDetail() {
  return {
    meta: meta(),
    profile: doctorRoi().rows[0],
    engagementHistory: [{ requestId: "REQ-1", interventionName: "Diabetes CME", interventionType: "CME", month: "2026-05", actualInterventionDate: "2026-05-10", totalRoiSpendUsd: 0, fxRateStatus: "official" }],
    prescriptionTrend: [{ month: "2026-05", ciplaPrescriptionQty: 100, competitorPrescriptionQty: 50, totalPrescriptionQty: 150 }],
    brandMix: [],
  };
}

function executionSummary() {
  return {
    meta: meta(),
    plannedEvents: 0,
    matchedEvents: 0,
    weakOrUnmatchedEvents: 0,
    executedEvents: 0,
    actionDueEvents: 0,
    plannedEventsWithExecutedEvidence: 0,
    plannedEventsWithActionDueEvidence: 0,
    executedSnapshotCount: 0,
    actionDueSnapshotCount: 0,
    plannedHcps: 0,
    engagedHcps: 0,
    matchedEngagedHcps: 0,
    rawEngagedHcps: 0,
    hcpExecutionRate: 0,
    eventExecutionRate: 0,
    matchCoverage: 0,
    snapshotSourceCounts: {},
    primaryScope: true,
    scopeStatuses: [],
    scopeReasons: [],
  };
}

function workflowSummary() {
  return {
    meta: meta(),
    requestApprovalCounts: {},
    requestConfirmationCounts: {},
    postApprovalCounts: {},
    postConfirmationCounts: {},
    ownerStageCounts: {},
    pendingRequestCount: 0,
    pendingReportCount: 0,
    reportsSentForCorrection: 0,
    reportsApproved: 0,
    expenseSubmittedCoverage: 0,
    expenseConfirmedCoverage: 0,
    primaryScope: true,
    scopeStatuses: [],
    scopeReasons: [],
  };
}
