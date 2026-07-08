import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("AI assistant", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a Gemini-backed grounded answer with dashboard pointers and limitations", async () => {
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

    await waitFor(() => expect(screen.getByRole("button", { name: /open execai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open execai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Business question"), {
      target: { value: "Where is execution risk highest?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));

    await waitFor(() => expect(screen.getByText("Review weak matches first.")).toBeInTheDocument());
    expect(screen.queryByText(/\*\*Execution risk\*\*/i)).not.toBeInTheDocument();
    expect(screen.getByText(/gemini-test/i)).toBeInTheDocument();
    expect(screen.getByText("Evidence used")).toBeInTheDocument();
    expect(screen.getByText("Weak/unmatched execution rows")).toBeInTheDocument();
    expect(screen.queryByText("execution.weakOrUnmatchedEvents")).not.toBeInTheDocument();
    expect(screen.getByText("ExecAI evidence workflow")).toBeInTheDocument();
    expect(screen.getByText("Where to verify this")).toBeInTheDocument();
    expect(screen.getByText("Execution event matrix table")).toBeInTheDocument();
    expect(screen.queryByText("execution: weak or unmatched events")).not.toBeInTheDocument();
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

    await waitFor(() => expect(screen.getByRole("button", { name: /open execai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open execai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Where is execution risk highest?" }));

    await waitFor(() => expect(screen.getByText("Safe fallback")).toBeInTheDocument());
    expect(screen.getByText("Review weak matches first.")).toBeInTheDocument();
  });

  it("does not crash when backend still returns old supportingMetrics shape", async () => {
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
      if (url.includes("/api/ai/query")) {
        return ok({
          answer: "Old backend response still answered.",
          supportingMetrics: [{ label: "execution: weak or unmatched events", value: 4, source: "execution" }],
          confidence: "medium",
          providerUsed: "gemini",
          modelUsed: "old-model",
          fallbackUsed: false,
          redactionApplied: false,
          contextScope: { pageContext: "execution", filters: {}, topN: 5, maxCharacters: 9000, sections: [] },
        });
      }
      return ok({});
    });

    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /open execai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open execai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Where is execution risk highest?" }));

    await waitFor(() => expect(screen.getByText("Old backend response still answered.")).toBeInTheDocument());
    expect(screen.getByText("Restart backend if dashboard pointers are missing repeatedly.")).toBeInTheDocument();
    expect(screen.queryByText("execution: weak or unmatched events")).not.toBeInTheDocument();
  });

  it("shows a contained warning for malformed AI responses", async () => {
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
      if (url.includes("/api/ai/query")) return ok({ providerUsed: "gemini" });
      return ok({});
    });

    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /open execai/i })).toBeInTheDocument(), { timeout: 5000 });
    fireEvent.click(screen.getByRole("button", { name: /open execai/i }));
    await waitFor(() => expect(screen.getByText("Ask the dashboard")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Where is execution risk highest?" }));

    await waitFor(() => expect(screen.getByText(/AI response was incomplete/i)).toBeInTheDocument());
    expect(screen.getByText(/Restart the backend/i)).toBeInTheDocument();
  });
});

function aiResponse({ fallbackUsed, providerUsed }: { fallbackUsed: boolean; providerUsed: string }) {
  return {
    answer: "Execution risk is concentrated in pending reports.",
    answerMarkdown: "**Execution risk** is concentrated in pending reports.\n\n- Review weak matches first.\n- Then verify pending reports.",
    evidenceRefs: [
      {
        section: "execution",
        label: "Weak/unmatched execution rows",
        value: 4,
        sourcePath: "execution.weakOrUnmatchedEvents",
      },
    ],
    agentSteps: [
      { step: "Planned query topics: execution.", status: "completed" },
      { step: "Retrieved bounded structured dashboard evidence before using the model.", status: "completed" },
    ],
    dashboardPointers: [
      {
        page: "Execution",
        section: "Execution event matrix table",
        detail: "Sort/filter the event rows by match status, execution status, unmatched reason, country, and month.",
        reason: "Specific event-level questions need row evidence, not just summary cards.",
      },
    ],
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
