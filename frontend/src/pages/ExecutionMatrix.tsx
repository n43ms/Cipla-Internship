import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Clock3, FileWarning, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { getExecutionEvents, getExecutionFilterOptions, getExecutionSummary } from "../api/execution";
import { getInterventionMix } from "../api/interventions";
import { getWorkflowRequests, getWorkflowSummary } from "../api/workflow";
import { ConfidenceBadge, SourceDerivationBadge, StatusBadge } from "../components/execution/ExecutionBadges";
import { InterventionMixChart, InterventionMixTable } from "../components/interventions/InterventionMixComponents";
import { WorkflowGovernanceCards, WorkflowStatusTable } from "../components/workflow/WorkflowComponents";
import type { ExecutionEventRow, WorkflowRequestRow, WorkflowSummaryResponse } from "../types/api";

const PAGE_SIZE = 25;
const WORKFLOW_PAGE_SIZE = 8;

type Filters = {
  country: string;
  month: string;
  includeOutOfScope: boolean;
};

export function ExecutionMatrix() {
  const [filters, setFilters] = useState<Filters>({ country: "", month: "", includeOutOfScope: false });
  const [page, setPage] = useState(1);
  const [selectedRow, setSelectedRow] = useState<ExecutionEventRow | null>(null);
  const [hasAppliedInitialScope, setHasAppliedInitialScope] = useState(false);
  const activeFilters = useMemo(
    () => ({
      country: filters.country || undefined,
      month: filters.month || undefined,
      includeOutOfScope: filters.includeOutOfScope || undefined,
    }),
    [filters.country, filters.month, filters.includeOutOfScope],
  );
  const workflowFilters = useMemo(
    () => ({
      country: filters.country || undefined,
      month: filters.month || undefined,
      includeOutOfScope: filters.includeOutOfScope || undefined,
    }),
    [filters.country, filters.month, filters.includeOutOfScope],
  );

  const filterOptions = useQuery({
    queryKey: ["execution-filter-options"],
    queryFn: getExecutionFilterOptions,
  });
  const summary = useQuery({
    queryKey: ["execution-summary", activeFilters],
    queryFn: () => getExecutionSummary(activeFilters),
  });
  const events = useQuery({
    queryKey: ["execution-events", activeFilters, page],
    queryFn: () => getExecutionEvents({ ...activeFilters, page, pageSize: PAGE_SIZE }),
  });
  const workflow = useQuery({
    queryKey: ["workflow-summary", workflowFilters],
    queryFn: () => getWorkflowSummary(workflowFilters),
  });
  const workflowRequests = useQuery({
    queryKey: ["workflow-requests", workflowFilters],
    queryFn: () => getWorkflowRequests({ ...workflowFilters, page: 1, pageSize: WORKFLOW_PAGE_SIZE }),
  });
  const interventions = useQuery({
    queryKey: ["intervention-mix", activeFilters],
    queryFn: () => getInterventionMix(activeFilters),
  });

  useEffect(() => {
    if (hasAppliedInitialScope || filters.month || !filterOptions.data?.recommendedMonth?.value) {
      return;
    }
    setFilters((current) => ({ ...current, month: filterOptions.data.recommendedMonth?.value ?? "" }));
    setHasAppliedInitialScope(true);
  }, [filterOptions.data?.recommendedMonth, filters.month, hasAppliedInitialScope]);

  const isLoading =
    filterOptions.isLoading ||
    summary.isLoading ||
    events.isLoading ||
    workflow.isLoading ||
    workflowRequests.isLoading ||
    interventions.isLoading;
  const isError =
    filterOptions.isError ||
    summary.isError ||
    events.isError ||
    workflow.isError ||
    workflowRequests.isError ||
    interventions.isError;

  if (isLoading) {
    return <PageState title="Loading execution governance" body="Fetching execution, workflow, and intervention evidence." />;
  }

  if (isError) {
    return <PageState title="Execution governance unavailable" body="The backend could not return one or more Phase 4 APIs." />;
  }

  const summaryData = summary.data;
  const eventRows = events.data?.rows ?? [];
  const workflowData = workflow.data;
  const workflowRows = workflowRequests.data?.rows ?? [];
  const interventionRows = interventions.data?.rows ?? [];
  const totalEvents = events.data?.total ?? 0;
  const pageCount = Math.max(Math.ceil(totalEvents / PAGE_SIZE), 1);
  const scopeLabel = [selectedLabel(filterOptions.data?.countries, filters.country), selectedLabel(filterOptions.data?.months, filters.month)]
    .filter(Boolean)
    .join(" | ") || "Nepal and Sri Lanka | Apr-May 2026";

  return (
    <main className="min-h-screen bg-surface text-ink">
      <section className="mx-auto max-w-7xl px-6 py-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-accent">Execution governance</p>
            <h1 className="mt-2 text-3xl font-semibold">Planned vs actual execution</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
              Reconciles yearly planner events, monthly execution snapshots, consolidation requests, lifecycle status, and intervention mix.
            </p>
            <p className="mt-3 text-sm font-medium text-slate-700">
              Scope: {scopeLabel}
              {filters.includeOutOfScope ? " including audit-only out-of-scope rows" : ""}
            </p>
          </div>
          {summaryData ? <SourceDerivationBadge sourceCounts={summaryData.snapshotSourceCounts} /> : null}
        </div>

        <FilterPanel
          countries={filterOptions.data?.countries ?? []}
          filters={filters}
          months={filterOptions.data?.months ?? []}
          onChange={(next) => {
            setHasAppliedInitialScope(true);
            setFilters((current) => ({ ...current, ...next }));
            setPage(1);
          }}
          recommendedMonth={filterOptions.data?.recommendedMonth ?? null}
        />

        <ScopeCoverageCards includeOutOfScope={filters.includeOutOfScope} scopeReasons={summaryData?.scopeReasons ?? []} />

        <QualityPanel
          flags={summaryData?.meta.dataQualityFlags ?? []}
          limitations={[
            ...(summaryData?.meta.limitations ?? []),
            ...(events.data?.meta.limitations ?? []),
            ...(workflowData?.meta.limitations ?? []),
            ...(interventions.data?.meta.limitations ?? []),
          ]}
          sourceNotes={summaryData?.meta.sourceDerivationNotes ?? []}
          weakOrUnmatched={summaryData?.weakOrUnmatchedEvents ?? 0}
        />

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <KpiCard icon={<FileWarning size={18} />} label="Planned events" value={formatCount(summaryData?.plannedEvents ?? 0)} />
          <KpiCard icon={<CheckCircle2 size={18} />} label="Matched plan/request evidence" value={formatCount(summaryData?.matchedEvents ?? 0)} />
          <KpiCard icon={<RefreshCw size={18} />} label="Executed planned events" value={formatCount(summaryData?.plannedEventsWithExecutedEvidence ?? summaryData?.executedEvents ?? 0)} />
          <KpiCard icon={<Clock3 size={18} />} label="Action-due planned events" value={formatCount(summaryData?.plannedEventsWithActionDueEvidence ?? summaryData?.actionDueEvents ?? 0)} />
          <KpiCard icon={<AlertTriangle size={18} />} label="Match coverage" value={formatPercent(summaryData?.matchCoverage ?? 0)} />
          <KpiCard icon={<CheckCircle2 size={18} />} label="Event execution" value={formatPercent(summaryData?.eventExecutionRate ?? 0)} />
        </div>

        <div className="mt-6 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
          <PlannedVsEngagedChart
            planned={summaryData?.plannedHcps ?? 0}
            engaged={summaryData?.matchedEngagedHcps ?? summaryData?.engagedHcps ?? 0}
            rate={summaryData?.hcpExecutionRate ?? 0}
            rawEngaged={summaryData?.rawEngagedHcps ?? 0}
            executedSnapshots={summaryData?.executedSnapshotCount ?? 0}
            actionDueSnapshots={summaryData?.actionDueSnapshotCount ?? 0}
          />
          <WorkflowPanel workflowData={workflowData} />
        </div>

        <div className="mt-6 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
          <InterventionMixChart rows={interventionRows} />
          <InterventionMixTable rows={interventionRows} />
        </div>

        <div className="mt-6 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
          <WorkflowRequestTable rows={workflowRows} total={workflowRequests.data?.total ?? 0} />
          <EventMatrixTable
            rows={eventRows}
            page={page}
            pageCount={pageCount}
            total={totalEvents}
            onPageChange={setPage}
            onSelect={setSelectedRow}
          />
        </div>
      </section>

      <EventDrawer row={selectedRow} onClose={() => setSelectedRow(null)} />
    </main>
  );
}

function FilterPanel({
  countries,
  filters,
  months,
  onChange,
  recommendedMonth,
}: {
  countries: { value: string; label: string }[];
  filters: Filters;
  months: { value: string; label: string }[];
  onChange: (filters: Partial<Filters>) => void;
  recommendedMonth: { value: string; label: string } | null;
}) {
  return (
    <div className="dashboard-card mt-6 p-4">
      <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
        <label className="text-sm font-medium text-slate-700">
          Country
          <select
            className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent"
            value={filters.country}
            onChange={(event) => onChange({ country: event.target.value })}
          >
            <option value="">All countries</option>
            {countries.map((country) => (
              <option key={country.value} value={country.value}>
                {country.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-700">
          Month
          <select
            className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-accent"
            value={filters.month}
            onChange={(event) => onChange({ month: event.target.value })}
          >
            <option value="">All months</option>
            {months.map((month) => (
              <option key={month.value} value={month.value}>
                {month.label}
              </option>
            ))}
          </select>
        </label>
        <button
          className="soft-button self-end rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          type="button"
          onClick={() => onChange({ country: "", month: "", includeOutOfScope: false })}
        >
          Clear
        </button>
      </div>
      <label className="mt-4 flex items-start gap-2 text-sm text-slate-700">
        <input
          className="mt-1"
          type="checkbox"
          checked={filters.includeOutOfScope}
          onChange={(event) => onChange({ includeOutOfScope: event.target.checked })}
        />
        <span>
          Include audit-only out-of-scope rows
          <span className="block text-xs text-muted">
            Keeps Malaysia, Myanmar, Oman, UAE, historical consolidation, and future planner rows visible for audit without mixing them into default Phase 4 KPIs.
          </span>
        </span>
      </label>
      {recommendedMonth ? (
        <p className="mt-3 text-xs text-muted">
          The page opens on {recommendedMonth.label} because it is the latest month with planner, snapshot, and consolidation evidence.
        </p>
      ) : null}
    </div>
  );
}

function ScopeCoverageCards({ includeOutOfScope, scopeReasons }: { includeOutOfScope: boolean; scopeReasons: string[] }) {
  return (
    <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <KpiCard icon={<CheckCircle2 size={18} />} label="Planner coverage" value="Nepal, Sri Lanka" />
      <KpiCard icon={<CheckCircle2 size={18} />} label="Snapshot coverage" value="Apr-May 2026" />
      <KpiCard icon={<CheckCircle2 size={18} />} label="Consolidation coverage" value="Scoped by API" />
      <div className="dashboard-card p-4">
        <div className="flex items-center gap-2 text-muted">
          <AlertTriangle size={18} />
          <p className="text-sm">Out-of-scope policy</p>
        </div>
        <p className="mt-3 text-sm font-medium">
          {includeOutOfScope ? "Audit rows visible" : "Excluded from KPI math"}
        </p>
        {scopeReasons.length > 0 ? <p className="mt-2 text-xs text-muted">{scopeReasons[0]}</p> : null}
      </div>
    </div>
  );
}

function QualityPanel({
  flags,
  limitations,
  sourceNotes,
  weakOrUnmatched,
}: {
  flags: string[];
  limitations: string[];
  sourceNotes: string[];
  weakOrUnmatched: number;
}) {
  const messages = [
    ...sourceNotes,
    ...limitations,
    ...(flags.includes("weak_or_unmatched_events") || weakOrUnmatched > 0
      ? [`${formatCount(weakOrUnmatched)} weak or unmatched reconciliation records require review before treating execution coverage as final.`]
      : []),
  ];
  if (messages.length === 0) {
    return (
      <div className="mt-5 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800 transition duration-200 ease-out">
        No Phase 4 data-quality limitations are reported for this scope.
      </div>
    );
  }
  return (
    <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 transition duration-200 ease-out">
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 shrink-0" size={16} />
        <div>
          <p className="font-medium">Use this dashboard as auditable governance, not final truth, until open records are reviewed.</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {Array.from(new Set(messages)).map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function PlannedVsEngagedChart({
  planned,
  engaged,
  rate,
  rawEngaged,
  executedSnapshots,
  actionDueSnapshots,
}: {
  planned: number;
  engaged: number;
  rate: number;
  rawEngaged: number;
  executedSnapshots: number;
  actionDueSnapshots: number;
}) {
  const data = [{ name: "HCPs", planned, engaged }];
  return (
    <div className="dashboard-card p-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="font-medium">Planned vs engaged HCPs</h2>
          <p className="text-sm text-muted">Matched execution HCP rate: {formatPercent(rate)}</p>
          <p className="mt-1 text-xs text-muted">
            Raw snapshot evidence: {formatCount(executedSnapshots)} executed snapshots, {formatCount(actionDueSnapshots)} action-due snapshots, {formatCount(rawEngaged)} total raw engaged HCPs.
          </p>
        </div>
      </div>
      <div className="chart-frame h-[20rem] sm:h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} width={48} />
            <Tooltip formatter={(value) => formatCount(Number(value))} />
            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
            <Bar dataKey="planned" fill="#2563eb" radius={[4, 4, 0, 0]} />
            <Bar dataKey="engaged" fill="#16a34a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function WorkflowPanel({ workflowData }: { workflowData: WorkflowSummaryResponse | undefined }) {
  return (
    <div className="space-y-4">
      <WorkflowGovernanceCards
        pendingRequests={workflowData?.pendingRequestCount ?? 0}
        pendingReports={workflowData?.pendingReportCount ?? 0}
        reportsApproved={workflowData?.reportsApproved ?? 0}
        reportsSentForCorrection={workflowData?.reportsSentForCorrection ?? 0}
      />
      <div className="grid gap-4 md:grid-cols-2">
        <WorkflowStatusTable title="Request approval" counts={workflowData?.requestApprovalCounts ?? {}} />
        <WorkflowStatusTable title="Request confirmation" counts={workflowData?.requestConfirmationCounts ?? {}} />
        <WorkflowStatusTable title="Post approval" counts={workflowData?.postApprovalCounts ?? {}} />
        <WorkflowStatusTable title="Post confirmation" counts={workflowData?.postConfirmationCounts ?? {}} />
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <CoverageCard label="Expense submitted coverage" value={workflowData?.expenseSubmittedCoverage ?? 0} />
        <CoverageCard label="Expense confirmed coverage" value={workflowData?.expenseConfirmedCoverage ?? 0} />
      </div>
      <WorkflowStatusTable title="Current blocker / owner stage" counts={workflowData?.ownerStageCounts ?? {}} />
    </div>
  );
}

function CoverageCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="dashboard-card p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{formatPercent(value)}</p>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-accent" style={{ width: `${Math.max(0, Math.min(value, 1)) * 100}%` }} />
      </div>
    </div>
  );
}

function EventMatrixTable({
  rows,
  page,
  pageCount,
  total,
  onPageChange,
  onSelect,
}: {
  rows: ExecutionEventRow[];
  page: number;
  pageCount: number;
  total: number;
  onPageChange: (page: number) => void;
  onSelect: (row: ExecutionEventRow) => void;
}) {
  return (
    <div className="dashboard-card">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-4">
        <div>
          <h2 className="font-medium">Event execution matrix</h2>
          <p className="text-sm text-muted">Reconciled planner, execution snapshot, and consolidation evidence with scoped unmatched reasons.</p>
        </div>
        <p className="text-sm text-muted">{formatCount(total)} rows</p>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">
          No execution rows match the current filters. If you selected an out-of-scope market or month, enable audit-only rows to inspect preserved source data.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[960px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Event</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Match</th>
                <th className="px-4 py-3">Reason / scope</th>
                <th className="px-4 py-3">HCPs</th>
                <th className="px-4 py-3">Execution</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Drilldown</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.sourceType}-${row.eventName}-${row.matchStatus}-${index}`} className="border-t border-slate-100">
                  <td className="px-4 py-3">
                    <div className="font-medium">{row.eventName ?? "Unnamed event"}</div>
                    <div className="text-xs text-muted">
                      {row.eventType ?? "No type"} | {row.country} | {row.month}
                    </div>
                    {row.sourceDerivationNote ? <div className="mt-1 text-xs text-amber-700">{row.sourceDerivationNote}</div> : null}
                  </td>
                  <td className="px-4 py-3">{row.sourceType.replaceAll("_", " ")}</td>
                  <td className="px-4 py-3">
                    <StatusBadge value={row.matchStatus} />
                    {row.matchGrain ? <div className="mt-1 text-xs text-muted">{humanize(row.matchGrain)}</div> : null}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-700">
                    <div>{reasonLabel(row)}</div>
                    {reasonDetail(row) ? (
                      <div className="mt-1 max-w-xs text-muted">{reasonDetail(row)}</div>
                    ) : null}
                  </td>
                  <td className="px-4 py-3">
                    {valueOrDash(row.plannedHcps)} planned / {valueOrDash(row.engagedHcps)} engaged
                  </td>
                  <td className="px-4 py-3">{row.executionStatus ?? row.snapshotSource ?? "No snapshot"}</td>
                  <td className="px-4 py-3">
                    <ConfidenceBadge value={row.confidence} />
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-sm font-medium text-accent hover:underline" type="button" onClick={() => onSelect(row)}>
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex items-center justify-between border-t border-slate-200 p-4 text-sm">
        <button
          className="soft-button rounded-md border border-slate-300 px-3 py-2 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none"
          type="button"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </button>
        <span className="text-muted">
          Page {page} of {pageCount}
        </span>
        <button
          className="soft-button rounded-md border border-slate-300 px-3 py-2 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none"
          type="button"
          disabled={page >= pageCount}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}

function WorkflowRequestTable({ rows, total }: { rows: WorkflowRequestRow[]; total: number }) {
  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between border-b border-slate-200 p-4">
        <div>
          <h2 className="font-medium">Workflow request drilldown</h2>
          <p className="text-sm text-muted">First {WORKFLOW_PAGE_SIZE} requests in the selected scope, including current blocker stage.</p>
        </div>
        <p className="text-sm text-muted">{formatCount(total)} requests</p>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">No workflow requests match the current filters.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1120px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Request</th>
                <th className="px-4 py-3">Rep / market</th>
                <th className="px-4 py-3">Intervention</th>
                <th className="px-4 py-3">Request status</th>
                <th className="px-4 py-3">Confirmation</th>
                <th className="px-4 py-3">Report status</th>
                <th className="px-4 py-3">Evidence dates</th>
                <th className="px-4 py-3">Scope</th>
                <th className="px-4 py-3">Current blocker</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.reqId ?? "request"}-${index}`} className="border-t border-slate-100">
                  <td className="px-4 py-3 font-medium">{row.reqId ?? "No request ID"}</td>
                  <td className="px-4 py-3">
                    <div>{row.repName ?? "Unknown rep"}</div>
                    <div className="text-xs text-muted">
                      {row.country} | {row.month}
                    </div>
                  </td>
                  <td className="px-4 py-3">{row.interventionType ?? "Unknown type"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge value={row.requestApprovalStatus} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge value={row.requestConfirmationStatus} />
                  </td>
                  <td className="space-y-1 px-4 py-3">
                    <StatusBadge value={row.postApprovalStatus} />
                    <StatusBadge value={row.postConfirmationStatus} />
                  </td>
                  <td className="px-4 py-3 text-xs text-muted">
                    <div>Submitted: {row.expenseSubmittedDate ?? "-"}</div>
                    <div>Confirmed: {row.expenseConfirmedDate ?? "-"}</div>
                  </td>
                  <td className="px-4 py-3 text-xs text-muted">
                    {row.isPrimaryPhase4Scope ? "Primary Phase 4" : humanize(row.scopeStatus ?? "audit_only")}
                  </td>
                  <td className="px-4 py-3">{row.currentOwnerStage ?? "unknown"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function EventDrawer({ row, onClose }: { row: ExecutionEventRow | null; onClose: () => void }) {
  if (!row) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/35 backdrop-blur-[1px] transition-opacity duration-200" role="dialog" aria-modal="true">
      <aside className="h-full w-full max-w-xl overflow-y-auto bg-white p-6 shadow-xl transition-transform duration-200">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-wide text-muted">Execution drilldown</p>
            <h2 className="mt-1 text-xl font-semibold">{row.eventName ?? "Unnamed event"}</h2>
          </div>
          <button className="soft-button rounded-md border border-slate-300 px-3 py-2 text-sm" type="button" onClick={onClose}>
            Close
          </button>
        </div>
        <dl className="mt-6 grid gap-4 text-sm">
          <Detail label="Country" value={row.country} />
          <Detail label="Month" value={row.month} />
          <Detail label="Source type" value={row.sourceType} />
          <Detail label="Match status" value={row.matchStatus} />
          <Detail label="Match grain" value={row.matchGrain ? humanize(row.matchGrain) : "Single or not applicable"} />
          <Detail label="Unmatched reason" value={row.unmatchedReasonCode ? humanize(row.unmatchedReasonCode) : "Not unmatched"} />
          <Detail label="Reason detail" value={row.unmatchedReasonDetail ?? row.scopeReason ?? "No additional detail"} />
          <Detail label="Phase 4 scope" value={row.isPrimaryPhase4Scope ? "Primary Phase 4 scope" : humanize(row.scopeStatus ?? "out_of_scope")} />
          <Detail label="Candidate match" value={row.candidateMatch ?? "None"} />
          <Detail label="Execution status" value={row.executionStatus ?? "No snapshot"} />
          <Detail label="HCPs" value={`${valueOrDash(row.plannedHcps)} planned / ${valueOrDash(row.engagedHcps)} engaged`} />
        </dl>
        <div className="mt-6 rounded-lg bg-slate-50 p-4">
          <h3 className="font-medium">Source references</h3>
          <pre className="mt-3 whitespace-pre-wrap break-words text-xs text-slate-700">{JSON.stringify(row.sourceReferences, null, 2)}</pre>
        </div>
      </aside>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-muted">{label}</dt>
      <dd className="mt-1 font-medium">{value}</dd>
    </div>
  );
}

function KpiCard({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="dashboard-card p-4">
      <div className="flex items-center gap-2 text-muted">
        {icon}
        <p className="text-sm">{label}</p>
      </div>
      <p className="mt-3 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function PageState({ title, body }: { title: string; body: string }) {
  return (
    <main className="min-h-screen bg-surface text-ink">
      <section className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="mt-3 text-muted">{body}</p>
      </section>
    </main>
  );
}

function selectedLabel(options: { value: string; label: string }[] | undefined, value: string) {
  if (!value) {
    return "";
  }
  return options?.find((option) => option.value === value)?.label ?? value;
}

function formatCount(value: number) {
  return new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function valueOrDash(value: number | null | undefined) {
  return value === null || value === undefined ? "-" : formatCount(value);
}

function reasonLabel(row: ExecutionEventRow) {
  if (row.unmatchedReasonCode) {
    return humanize(row.unmatchedReasonCode);
  }
  if (row.isPrimaryPhase4Scope) {
    return row.matchStatus === "matched" ? "Matched evidence" : "In scoped evidence set";
  }
  return row.scopeStatus ? humanize(row.scopeStatus) : "Audit-only row";
}

function reasonDetail(row: ExecutionEventRow) {
  if (row.unmatchedReasonDetail) {
    return row.unmatchedReasonDetail;
  }
  if (!row.isPrimaryPhase4Scope) {
    return row.scopeReason ?? null;
  }
  return null;
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
