import { screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DataQuality } from "../src/pages/DataQuality";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("Data Quality page", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders validation, unmatched, workflow, intervention, and FX drilldowns", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/data-quality")) return ok(dataQuality());
      return ok({});
    });

    renderWithProviders(<DataQuality />);

    await waitFor(() => expect(screen.getByText("Data quality")).toBeInTheDocument());
    expect(screen.getByText("Loaded files")).toBeInTheDocument();
    expect(screen.getByText("Match coverage")).toBeInTheDocument();
    expect(screen.getByText("Pcode coverage")).toBeInTheDocument();
    expect(screen.getByText("RCPA coverage")).toBeInTheDocument();
    expect(screen.getByText("Missing FX")).toBeInTheDocument();
    expect(screen.getByText("Workflow coverage")).toBeInTheDocument();
    expect(screen.getByText("Source file participation")).toBeInTheDocument();
    expect(screen.getByText("FX quality")).toBeInTheDocument();
    expect(screen.getByText("Unmatched by source")).toBeInTheDocument();
    expect(screen.getByText("Unmatched records")).toBeInTheDocument();
    expect(screen.getByText("Validation drilldown")).toBeInTheDocument();
    expect(screen.getByText("missing_field")).toBeInTheDocument();
    expect(screen.getAllByText("planner only").length).toBeGreaterThanOrEqual(1);
  });
});

function dataQuality() {
  return {
    meta: {
      generatedAt: "2026-06-19T00:00:00Z",
      latestIngestionStatus: "completed_with_warnings",
      filtersApplied: {},
      dataQualityFlags: ["weak_match_coverage", "provisional_fx"],
      limitations: ["Some rows use provisional FX."],
      sourceDerivationNotes: [],
    },
    latestIngestion: { id: "run-1", status: "completed_with_warnings", startedAt: null, completedAt: null, sourceFileCount: 8, totalRowsSeen: 10, totalRowsLoaded: 9, totalRowsSkipped: 1, warningCount: 1, errorCount: 0 },
    sourceFileCount: 8,
    loadedFileCount: 8,
    rowsSeen: 10,
    rowsLoaded: 9,
    rowsSkipped: 1,
    validationErrorCount: 0,
    validationWarningCount: 1,
    matchCoverage: 0.6138,
    pcodeCoverage: 1,
    rcpaCoverage: 0.9926,
    missingFxCount: 0,
    provisionalFxCount: 1555,
    btuBtcReconciliationIssueCount: 0,
    missingConfirmedAmountCount: 0,
    spendWithoutPlanCount: 0,
    planWithoutSpendCount: 1,
    requestWorkflowCoverage: 1,
    postWorkflowCoverage: 0.7,
    interventionTypeCoverage: 1,
    unmatchedEventCount: 158,
    derivedSnapshotCount: 31,
    serialMonthParseCount: 0,
    staticFxSeedDate: "2026-06-16",
    officialLkrRateToUsd: 0.0032258065,
    actualAttendanceMissingPcodeCount: 0,
    unallocatedDoctorSpendLocal: 0,
    unallocatedDoctorSpendUsd: 0,
    staleIngestion: false,
    validationIssues: [{ severity: "warning", sourceFile: "planner.xlsx", sheetName: "YP FY27", rowNumber: 10, entityType: "plan_event", fieldName: "country", errorCode: "missing_field", message: "Missing optional country field" }],
    sourceFiles: [{ sourceFile: "planner.xlsx", sourceType: "planner", status: "completed_with_warnings", rowsSeen: 10, rowsLoaded: 9, rowsSkipped: 1, warningCount: 1, errorCount: 0, periodStart: null, periodEnd: null }],
    unmatchedBySource: [{ sourceType: "planner", reasonCode: "planner_only", recordCount: 2 }],
    unmatchedRecords: [{ sourceType: "planner", country: "Sri Lanka", month: "2026-05", eventName: "Unmatched CME", eventType: "CME", reasonCode: "planner_only", reasonDetail: "No request", candidateMatch: null, confidence: 0 }],
    fxQuality: [{ currencyCode: "LKR", rateStatus: "official", rateToUsd: 0.0032258065, rateDate: "2026-06-16", source: "company", rowCount: 1 }],
  };
}
