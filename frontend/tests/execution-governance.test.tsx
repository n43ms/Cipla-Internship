import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("Execution governance page", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders execution, derived-source, workflow pending, and intervention states", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/execution/filter-options")) {
        return ok({
          countries: [{ value: "LK", label: "Sri Lanka" }],
          months: [{ value: "2026-05", label: "2026-05" }],
          recommendedMonth: { value: "2026-05", label: "2026-05" },
        });
      }
      if (url.includes("/api/execution/summary")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", dataQualityFlags: ["weak_or_unmatched_events"], limitations: [], sourceDerivationNotes: [] },
          plannedEvents: 2,
          matchedEvents: 1,
          weakOrUnmatchedEvents: 1,
          executedEvents: 1,
          actionDueEvents: 1,
          plannedEventsWithExecutedEvidence: 1,
          plannedEventsWithActionDueEvidence: 1,
          executedSnapshotCount: 1,
          actionDueSnapshotCount: 1,
          plannedHcps: 10,
          engagedHcps: 5,
          matchedEngagedHcps: 5,
          rawEngagedHcps: 5,
          hcpExecutionRate: 0.5,
          eventExecutionRate: 0.5,
          matchCoverage: 0.5,
          snapshotSourceCounts: { derived_from_consolidation: 1 },
          primaryScope: true,
          scopeStatuses: ["primary_phase4_scope"],
          scopeReasons: ["Primary Phase 4 scope: planner, execution snapshot, and consolidation evidence are all available."],
        });
      }
      if (url.includes("/api/workflow/summary")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", dataQualityFlags: [], limitations: [] },
          requestApprovalCounts: { approved: 1 },
          requestConfirmationCounts: { confirmed: 1 },
          postApprovalCounts: { pending_owner: 1 },
          postConfirmationCounts: { draft: 1 },
          ownerStageCounts: { manager: 1 },
          pendingRequestCount: 0,
          pendingReportCount: 1,
          reportsSentForCorrection: 0,
          reportsApproved: 0,
          expenseSubmittedCoverage: 1,
          expenseConfirmedCoverage: 0,
          primaryScope: true,
          scopeStatuses: ["primary_phase4_scope"],
          scopeReasons: ["Primary Phase 4 scope."],
        });
      }
      if (url.includes("/api/workflow/requests")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", dataQualityFlags: [], limitations: [] },
          page: 1,
          pageSize: 8,
          total: 1,
          rows: [{
            reqId: "REQ-1",
            country: "Sri Lanka",
            month: "2026-05",
            repName: "Anil Arial",
            interventionType: "CME",
            requestApprovalStatus: "approved",
            requestConfirmationStatus: "approved",
            postApprovalStatus: "pending_owner",
            postConfirmationStatus: "draft",
            currentOwnerStage: "post report approval pending",
            expenseSubmittedDate: "2026-05-20",
            expenseConfirmedDate: null,
            isPrimaryPhase4Scope: true,
            scopeStatus: "primary_phase4_scope",
            scopeReason: "Primary Phase 4 scope.",
          }],
        });
      }
      return ok({
        meta: { generatedAt: "now", latestIngestionStatus: "completed", dataQualityFlags: [], limitations: [] },
        rows: [{
          interventionType: "CME",
          interventionSubType: "Local",
          requestCount: 1,
          executedCount: 1,
          executedRequestCount: 1,
          matchedRequestCount: 1,
          executedSnapshotCount: 1,
          actionDueCount: 0,
          actionDueRequestCount: 0,
          actionDueSnapshotCount: 0,
          matchedWithoutExecutionCount: 0,
          approvedCount: 1,
          reportPendingCount: 1,
          confirmedContractedAmount: 100,
          directHcpBtuSpend: 50,
          overheadBtcSpend: 20,
          totalActualSpend: 70,
          fxRateStatus: "official",
        }],
      });
    });

    renderWithProviders(<App />);

    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));
    await waitFor(
      () => expect(screen.getByText("Planned vs actual execution")).toBeInTheDocument(),
      { timeout: 10000 },
    );
    await waitFor(
      () => expect(screen.getByText("Scope: 2026-05")).toBeInTheDocument(),
      { timeout: 10000 },
    );
    expect(screen.queryByText("Planner coverage")).not.toBeInTheDocument();
    expect(screen.queryByText("Snapshot coverage")).not.toBeInTheDocument();
    expect(screen.queryByText("Out-of-scope policy")).not.toBeInTheDocument();
    expect(screen.getByText(/The page opens on 2026-05/)).toBeInTheDocument();
    expect(screen.getByText(/Default KPIs use Nepal\/Sri Lanka Apr-May planner coverage/)).toBeInTheDocument();
    expect(screen.getByText("1 derived from consolidation")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /open data warning notes/i }));
    expect(screen.getByText("Execution evidence notes")).toBeInTheDocument();
    expect(screen.getByText(/weak or unmatched reconciliation records require review/)).toBeInTheDocument();
    expect(screen.getByText("Planned vs engaged HCPs")).toBeInTheDocument();
    expect(screen.queryByText("Event execution matrix")).not.toBeInTheDocument();
    expect(screen.getByText("Pending reports")).toBeInTheDocument();
    expect(screen.getByText("Expense coverage")).toBeInTheDocument();
    expect(screen.getByText("Request confirmation")).toBeInTheDocument();
    expect(screen.getByText("Post confirmation")).toBeInTheDocument();
    expect(screen.getByText("Intervention mix")).toBeInTheDocument();
    expect(screen.getByText("Intervention type mix")).toBeInTheDocument();
    expect(screen.getAllByText("Executed snapshots").length).toBeGreaterThan(0);
    expect(screen.getByText("Executed request links")).toBeInTheDocument();
    expect(screen.getByText("Workflow request drilldown")).toBeInTheDocument();
    expect(screen.getByText("Anil Arial")).toBeInTheDocument();
    expect(screen.getByText("Submitted: 2026-05-20")).toBeInTheDocument();
    expect(screen.getByText("Confirmed: -")).toBeInTheDocument();
    expect(screen.queryByText("Primary Phase 4")).not.toBeInTheDocument();
  });

  it("renders an API error state", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("fail", { status: 500 }));

    renderWithProviders(<App />);

    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));
    await waitFor(() => expect(screen.getByText("Execution governance unavailable")).toBeInTheDocument(), { timeout: 5000 });
  });

  it("renders empty matrix and sends selected filters", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/execution/filter-options")) {
        return ok({
          countries: [{ value: "LK", label: "Sri Lanka" }],
          months: [{ value: "2026-05", label: "2026-05" }],
        });
      }
      if (url.includes("/api/execution/summary")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", filtersApplied: {}, dataQualityFlags: [], limitations: [], sourceDerivationNotes: [] },
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
        });
      }
      if (url.includes("/api/workflow/summary")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", filtersApplied: {}, dataQualityFlags: [], limitations: [] },
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
        });
      }
      if (url.includes("/api/workflow/requests")) {
        return ok({
          meta: { generatedAt: "now", latestIngestionStatus: "completed", filtersApplied: {}, dataQualityFlags: [], limitations: [] },
          page: 1,
          pageSize: 8,
          total: 0,
          rows: [],
        });
      }
      return ok({ meta: { generatedAt: "now", latestIngestionStatus: "completed", filtersApplied: {}, dataQualityFlags: [], limitations: [] }, rows: [] });
    });

    renderWithProviders(<App />);

    fireEvent.click(screen.getByRole("button", { name: /click to continue/i }));
    await waitFor(() => expect(screen.getByText("Workflow request drilldown")).toBeInTheDocument());
    const countryInput = screen.getByLabelText("Country");
    fireEvent.change(countryInput, { target: { value: "LK" } });
    await waitFor(() => expect(screen.getByDisplayValue("Sri Lanka")).toBeInTheDocument());
    const monthInput = screen.getByLabelText("Month");
    fireEvent.change(monthInput, { target: { value: "2026-05" } });

    await waitFor(() => {
      const urls = fetchMock.mock.calls.map(([input]) => String(input));
      expect(urls.some((url) => url.includes("country=LK") && url.includes("month=2026-05"))).toBe(true);
      expect(urls.some((url) => url.includes("/api/execution/events"))).toBe(false);
    });
  });
});
