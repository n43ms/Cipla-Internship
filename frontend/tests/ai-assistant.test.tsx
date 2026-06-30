import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("AI assistant", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a Gemini-backed grounded answer with metrics and limitations", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((input, init) => {
      const url = String(input);
      if (url.includes("/api/data-quality")) return ok(dataQuality());
      if (url.includes("/api/filters")) return ok(filters());
      if (url.includes("/api/execution/filter-options")) return ok({ countries: [], months: [], recommendedMonth: null });
      if (url.includes("/api/execution/summary")) return ok(executionSummary());
      if (url.includes("/api/execution/events")) return ok({ meta: meta(), page: 1, pageSize: 25, total: 0, rows: [] });
      if (url.includes("/api/workflow/summary")) return ok(workflowSummary());
      if (url.includes("/api/workflow/requests")) return ok({ meta: meta(), page: 1, pageSize: 8, total: 0, rows: [] });
      if (url.includes("/api/interventions/mix")) return ok({ meta: meta(), rows: [] });
      if (url.includes("/api/ai/query")) {
        expect(JSON.parse(String(init?.body)).pageContext).toBe("execution");
        return ok(aiResponse({ fallbackUsed: false, providerUsed: "gemini" }));
      }
      return ok({});
    });

    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /open grounded ai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open grounded ai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Business question"), {
      target: { value: "Where is execution risk highest?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => expect(screen.getByText("Execution risk is concentrated in pending reports.")).toBeInTheDocument());
    expect(screen.getByText(/gemini-test/i)).toBeInTheDocument();
    expect(screen.getByText("execution: weak or unmatched events")).toBeInTheDocument();
    expect(screen.getByText("RCPA is historical baseline.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalled();
  });

  it("shows deterministic fallback status when provider credits fail", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/data-quality")) return ok(dataQuality());
      if (url.includes("/api/filters")) return ok(filters());
      if (url.includes("/api/execution/filter-options")) return ok({ countries: [], months: [], recommendedMonth: null });
      if (url.includes("/api/execution/summary")) return ok(executionSummary());
      if (url.includes("/api/execution/events")) return ok({ meta: meta(), page: 1, pageSize: 25, total: 0, rows: [] });
      if (url.includes("/api/workflow/summary")) return ok(workflowSummary());
      if (url.includes("/api/workflow/requests")) return ok({ meta: meta(), page: 1, pageSize: 8, total: 0, rows: [] });
      if (url.includes("/api/interventions/mix")) return ok({ meta: meta(), rows: [] });
      if (url.includes("/api/ai/query")) return ok(aiResponse({ fallbackUsed: true, providerUsed: "deterministic" }));
      return ok({});
    });

    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /open grounded ai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open grounded ai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Where is execution risk highest?" }));

    await waitFor(() => expect(screen.getByText("Safe fallback")).toBeInTheDocument());
    expect(screen.getByText("Execution risk is concentrated in pending reports.")).toBeInTheDocument();
  });
});

function aiResponse({ fallbackUsed, providerUsed }: { fallbackUsed: boolean; providerUsed: string }) {
  return {
    answer: "Execution risk is concentrated in pending reports.",
    supportingMetrics: [{ label: "execution: weak or unmatched events", value: 4, source: "execution" }],
    limitations: ["RCPA is historical baseline."],
    confidence: "medium",
    providerUsed,
    modelUsed: fallbackUsed ? "rules" : "gemini-test",
    fallbackUsed,
    redactionApplied: false,
    contextScope: {
      pageContext: "execution",
      filters: {},
      topN: 40,
      maxCharacters: 24000,
      sections: ["execution", "workflow"],
    },
  };
}

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
    serialMonthParseCount: 0,
    staticFxSeedDate: "2026-01-01",
    officialLkrRateToUsd: 0.0032258065,
    actualAttendanceMissingPcodeCount: 0,
    unallocatedDoctorSpendLocal: 0,
    unallocatedDoctorSpendUsd: 0,
    staleIngestion: false,
    validationIssues: [],
    sourceFiles: [],
    unmatchedBySource: [],
    unmatchedRecords: [],
    fxQuality: [],
  };
}

function filters() {
  return {
    countries: [{ value: "LK", label: "Sri Lanka" }],
    months: [{ value: "2026-05", label: "2026-05" }],
    interventionTypes: [],
    brands: [],
    specialities: [],
    doctorClasses: [],
    roiSegments: [],
    latestIngestionStatus: "completed",
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
