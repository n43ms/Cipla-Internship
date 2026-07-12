import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, Clock3, FileWarning, RefreshCw } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { getExecutionFilterOptions, getExecutionSummary } from "../api/execution";
import { getInterventionMix } from "../api/interventions";
import { getWorkflowRequests, getWorkflowSummary } from "../api/workflow";
import { SourceDerivationBadge, StatusBadge } from "../components/execution/ExecutionBadges";
import { InterventionMixChart, InterventionMixTable } from "../components/interventions/InterventionMixComponents";
import { WorkflowGovernanceCards, WorkflowStatusTable } from "../components/workflow/WorkflowComponents";
import { SmoothSelect } from "../components/common/SmoothSelect";
import { SidePanel } from "../components/common/SidePanel";
import { LoadingState } from "../components/common/DataStateComponents";
import { TableLoadingOverlay } from "../components/common/TableLoadingOverlay";
import { WarningRegistration } from "../components/common/WarningCenter";
import { nextSort, SortableHeader, type SortState } from "../components/common/SortableTable";
import type { WorkflowRequestRow, WorkflowSummaryResponse } from "../types/api";

const WORKFLOW_PAGE_SIZE = 8;

type WorkflowSortKey = "reqId" | "repName" | "interventionType" | "requestConfirmationStatus" | "postConfirmationStatus" | "expenseConfirmedDate" | "currentOwnerStage";

type Filters = {
  country: string;
  month: string;
  includeOutOfScope: boolean;
};

export function ExecutionMatrix({ onAiContextChange }: { onAiContextChange?: (context: { pageContext: string; filters: Record<string, unknown> }) => void }) {
  const [filters, setFilters] = useState<Filters>({ country: "", month: "", includeOutOfScope: false });
  const [hasAppliedInitialScope, setHasAppliedInitialScope] = useState(false);
  const [workflowSort, setWorkflowSort] = useState<SortState<WorkflowSortKey>>({ key: "reqId", direction: "asc" });
  const [workflowPage, setWorkflowPage] = useState(1);
  const [workflowSearchInput, setWorkflowSearchInput] = useState("");
  const [workflowSearch, setWorkflowSearch] = useState("");
  const [selectedWorkflowRequest, setSelectedWorkflowRequest] = useState<WorkflowRequestRow | null>(null);
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
      workflowSearch: workflowSearch || undefined,
    }),
    [filters.country, filters.month, filters.includeOutOfScope, workflowSearch],
  );

  const filterOptions = useQuery({
    queryKey: ["execution-filter-options"],
    queryFn: getExecutionFilterOptions,
  });
  const summary = useQuery({
    queryKey: ["execution-summary", activeFilters],
    queryFn: () => getExecutionSummary(activeFilters),
  });
  const workflow = useQuery({
    queryKey: ["workflow-summary", workflowFilters],
    queryFn: () => getWorkflowSummary(workflowFilters),
  });
  const workflowRequests = useQuery({
    queryKey: ["workflow-requests", workflowFilters, workflowPage, workflowSort],
    queryFn: () => getWorkflowRequests({ ...workflowFilters, page: workflowPage, pageSize: WORKFLOW_PAGE_SIZE, sort: workflowSort.key, sortDirection: workflowSort.direction }),
    placeholderData: (previousData) => previousData,
  });
  const interventions = useQuery({
    queryKey: ["intervention-mix", activeFilters],
    queryFn: () => getInterventionMix(activeFilters),
  });

  useEffect(() => {
    onAiContextChange?.({ pageContext: "execution", filters: activeFilters });
  }, [activeFilters, onAiContextChange]);

  useEffect(() => {
    if (hasAppliedInitialScope || filters.month || !filterOptions.data?.recommendedMonth?.value) {
      return;
    }
    setFilters((current) => ({ ...current, month: filterOptions.data.recommendedMonth?.value ?? "" }));
    setHasAppliedInitialScope(true);
  }, [filterOptions.data?.recommendedMonth, filters.month, hasAppliedInitialScope]);

  const isLoading =
    filterOptions.isLoading ||
    (summary.isLoading && !summary.data) ||
    (workflow.isLoading && !workflow.data) ||
    (workflowRequests.isLoading && !workflowRequests.data) ||
    (interventions.isLoading && !interventions.data);
  const isError =
    filterOptions.isError ||
    summary.isError ||
    workflow.isError ||
    workflowRequests.isError ||
    interventions.isError;

  if (isLoading) {
    return <main><LoadingState label="Loading execution governance" /></main>;
  }

  if (isError) {
    return <PageState title="Execution governance unavailable" body="The backend could not return one or more Phase 4 APIs. Please ensure the backend is up and running." />;
  }

  const summaryData = summary.data;
  const workflowData = workflow.data;
  const workflowRows = workflowRequests.data?.rows ?? [];
  const interventionRows = interventions.data?.rows ?? [];
  const scopeLabel = [selectedLabel(filterOptions.data?.countries, filters.country), selectedLabel(filterOptions.data?.months, filters.month)]
    .filter(Boolean)
    .join(" | ") || "Nepal and Sri Lanka | Apr-May 2026";

  return (
    <main className="min-h-screen animate-page-enter bg-surface text-ink">
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-accent">Execution governance</p>
            <h1 className="mt-2 text-3xl font-semibold">Planned vs actual execution</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
              Reconciles yearly planner events, monthly execution snapshots, consolidation requests, lifecycle status, and intervention mix.
            </p>
            <p className="mt-3 text-sm font-medium text-zinc-300">
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
            setWorkflowPage(1);
          }}
          recommendedMonth={filterOptions.data?.recommendedMonth ?? null}
        />

        <QualityPanel
          flags={summaryData?.meta.dataQualityFlags ?? []}
          limitations={[
            ...(summaryData?.meta.limitations ?? []),
            ...(workflowData?.meta.limitations ?? []),
            ...(interventions.data?.meta.limitations ?? []),
          ]}
          sourceNotes={summaryData?.meta.sourceDerivationNotes ?? []}
          weakOrUnmatched={summaryData?.weakOrUnmatchedEvents ?? 0}
        />

        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6">
          <KpiCard tone="sky" icon={<FileWarning size={18} />} label="Planned events" value={formatCount(summaryData?.plannedEvents ?? 0)} />
          <KpiCard tone="cyan" icon={<CheckCircle2 size={18} />} label="Matched plan/request evidence" value={formatCount(summaryData?.matchedEvents ?? 0)} />
          <KpiCard tone="emerald" icon={<RefreshCw size={18} />} label="Executed planned events" value={formatCount(summaryData?.plannedEventsWithExecutedEvidence ?? summaryData?.executedEvents ?? 0)} />
          <KpiCard tone="amber" icon={<Clock3 size={18} />} label="Action-due planned events" value={formatCount(summaryData?.plannedEventsWithActionDueEvidence ?? summaryData?.actionDueEvents ?? 0)} />
          <KpiCard tone="violet" icon={<AlertTriangle size={18} />} label="Match coverage" value={formatPercent(summaryData?.matchCoverage ?? 0)} />
          <KpiCard tone="emerald" icon={<CheckCircle2 size={18} />} label="Event execution" value={formatPercent(summaryData?.eventExecutionRate ?? 0)} />
        </div>

        <div className="mt-6">
          <PlannedVsEngagedChart
            planned={summaryData?.plannedHcps ?? 0}
            engaged={summaryData?.matchedEngagedHcps ?? summaryData?.engagedHcps ?? 0}
            rate={summaryData?.hcpExecutionRate ?? 0}
            rawEngaged={summaryData?.rawEngagedHcps ?? 0}
            executedSnapshots={summaryData?.executedSnapshotCount ?? 0}
            actionDueSnapshots={summaryData?.actionDueSnapshotCount ?? 0}
          />
        </div>

        <WorkflowPanel workflowData={workflowData} />

        <div className="mt-6 grid min-w-0 grid-cols-1 items-start gap-6">
          <InterventionMixChart rows={interventionRows} />
          <InterventionMixTable rows={interventionRows} />
        </div>

        <div className="mt-6 grid min-w-0 grid-cols-1 items-start gap-6">
          <WorkflowRequestTable
            rows={workflowRows}
            page={workflowRequests.data?.page ?? workflowPage}
            pageSize={workflowRequests.data?.pageSize ?? WORKFLOW_PAGE_SIZE}
            total={workflowRequests.data?.total ?? 0}
            sort={workflowSort}
            isFetching={workflowRequests.isFetching}
            workflowSearch={workflowSearchInput}
            onPageChange={setWorkflowPage}
            onSelect={setSelectedWorkflowRequest}
            onSort={(column) => { setWorkflowSort((current) => nextSort(current, column)); setWorkflowPage(1); }}
            onWorkflowSearchChange={setWorkflowSearchInput}
            onWorkflowSearchSubmit={() => { setWorkflowSearch(workflowSearchInput.trim()); setWorkflowPage(1); }}
          />
        </div>
      </section>
      <SidePanel open={Boolean(selectedWorkflowRequest)} onClose={() => setSelectedWorkflowRequest(null)} widthClass="max-w-lg">
        {selectedWorkflowRequest ? <WorkflowRequestDetail request={selectedWorkflowRequest} /> : null}
      </SidePanel>
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
    <div className="dashboard-card mt-6 overflow-visible p-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
        <div className="text-sm font-medium text-zinc-300">
          Country
          <SmoothSelect ariaLabel="Country" className="mt-1" value={filters.country} options={countries} placeholder="All countries" onChange={(country) => onChange({ country })} />
        </div>
        <div className="text-sm font-medium text-zinc-300">
          Month
          <SmoothSelect ariaLabel="Month" className="mt-1" value={filters.month} options={months} placeholder="All months" onChange={(month) => onChange({ month })} />
        </div>
        <button
          className="soft-button w-full self-end rounded-md border border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-300 hover:bg-zinc-950/70 md:w-auto"
          type="button"
          onClick={() => onChange({ country: "", month: "", includeOutOfScope: false })}
        >
          Clear
        </button>
      </div>
      <label className="mt-4 flex items-start gap-2 text-sm text-zinc-300">
        <input
          className="mt-1"
          type="checkbox"
          checked={filters.includeOutOfScope}
          onChange={(event) => onChange({ includeOutOfScope: event.target.checked })}
        />
        <span>
          Include audit-only out-of-scope rows
          <span className="block text-xs text-muted">
            Default KPIs use Nepal/Sri Lanka Apr-May planner coverage; switch this on only to audit preserved rows from other markets or periods.
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
  return (
    <WarningRegistration
      record={{
        id: "execution-evidence",
        title: "Execution evidence notes",
        detail: "Review before treating execution coverage as final",
        tone: "warning",
        items: messages,
      }}
    />
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
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={240} debounce={100}>
          <BarChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 28 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} width={48} />
            <Tooltip cursor={{ fill: "rgba(97, 199, 187, 0.075)" }} formatter={(value) => formatCount(Number(value))} />
            <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
            <Bar dataKey="planned" fill="#61c7bb" radius={[4, 4, 0, 0]} animationDuration={800} />
            <Bar dataKey="engaged" fill="#78c58a" radius={[4, 4, 0, 0]} animationDuration={800} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function WorkflowPanel({ workflowData }: { workflowData: WorkflowSummaryResponse | undefined }) {
  return (
    <section className="mt-6 space-y-4">
      <div>
        <h2 className="text-lg font-medium">Workflow governance</h2>
        <p className="mt-1 text-sm text-muted">Request, report, expense, and blocker status for the selected execution scope.</p>
      </div>
      <WorkflowGovernanceCards
        pendingRequests={workflowData?.pendingRequestCount ?? 0}
        pendingReports={workflowData?.pendingReportCount ?? 0}
        reportsApproved={workflowData?.reportsApproved ?? 0}
        reportsSentForCorrection={workflowData?.reportsSentForCorrection ?? 0}
      />
      <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-2 2xl:grid-cols-4">
        <WorkflowStatusTable title="Request confirmation" counts={workflowData?.requestConfirmationCounts ?? {}} />
        <WorkflowStatusTable title="Post confirmation" counts={workflowData?.postConfirmationCounts ?? {}} />
        <ExpenseCoveragePanel
          submitted={workflowData?.expenseSubmittedCoverage ?? 0}
          confirmed={workflowData?.expenseConfirmedCoverage ?? 0}
        />
        <WorkflowStatusTable title="Current blocker / owner stage" counts={workflowData?.ownerStageCounts ?? {}} maxEntries={6} />
      </div>
    </section>
  );
}

function ExpenseCoveragePanel({ confirmed, submitted }: { confirmed: number; submitted: number }) {
  return (
    <div className="dashboard-card flex h-full flex-col p-4">
      <h3 className="font-medium">Expense coverage</h3>
      <div className="mt-14 grid gap-4">
        <CoverageBar label="Submitted" value={submitted} />
        <CoverageBar label="Confirmed" value={confirmed} />
      </div>
    </div>
  );
}

function CoverageBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="text-muted">{label}</span>
        <span className="font-medium">{formatPercent(value)}</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-zinc-800">
        <div className="h-full rounded-full bg-accent" style={{ width: `${Math.max(0, Math.min(value, 1)) * 100}%` }} />
      </div>
    </div>
  );
}

function WorkflowRequestTable({
  rows,
  page,
  pageSize,
  total,
  sort,
  isFetching = false,
  workflowSearch,
  onPageChange,
  onSelect,
  onSort,
  onWorkflowSearchChange,
  onWorkflowSearchSubmit,
}: {
  rows: WorkflowRequestRow[];
  page: number;
  pageSize: number;
  total: number;
  sort: SortState<WorkflowSortKey>;
  isFetching?: boolean;
  workflowSearch: string;
  onPageChange: (page: number) => void;
  onSelect: (row: WorkflowRequestRow) => void;
  onSort: (column: WorkflowSortKey) => void;
  onWorkflowSearchChange: (value: string) => void;
  onWorkflowSearchSubmit: () => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return (
    <div className="dashboard-card relative overflow-hidden">
      <TableLoadingOverlay isFetching={isFetching} label="Refreshing workflow rows" />
      <div className="flex flex-col gap-3 border-b border-zinc-800 p-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="font-medium">Workflow request drilldown</h2>
          <p className="text-sm text-muted">Paged requests in the selected scope. Open a row for blocker owner and evidence dates.</p>
        </div>
        <form
          className="grid gap-1 text-sm lg:w-96"
          onSubmit={(event) => {
            event.preventDefault();
            onWorkflowSearchSubmit();
          }}
        >
          <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">Search request</span>
          <div className="flex gap-2">
            <input
              className="form-control min-w-0 flex-1"
              value={workflowSearch}
              placeholder="Request, rep, market, intervention, or blocker"
              onChange={(event) => onWorkflowSearchChange(event.target.value)}
            />
            <button type="submit" className="soft-button rounded-md border border-zinc-800 px-3 py-2 text-sm font-semibold text-zinc-200">Search</button>
          </div>
        </form>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">No workflow requests match the current filters.</p>
      ) : (
        <div className="table-scroll">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="table-head">
              <tr>
                <SortableHeader column="reqId" label="Request" sort={sort} onSort={onSort} />
                <SortableHeader column="repName" label="Rep / market" sort={sort} onSort={onSort} />
                <SortableHeader column="interventionType" label="Intervention" sort={sort} onSort={onSort} />
                <SortableHeader column="requestConfirmationStatus" label="Confirmation" sort={sort} onSort={onSort} />
                <SortableHeader column="postConfirmationStatus" label="Report status" sort={sort} onSort={onSort} />
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.reqId ?? "request"}-${index}`} className="table-row">
                  <td className="px-4 py-3 font-medium">{row.reqId ?? "No request ID"}</td>
                  <td className="px-4 py-3">
                    <div>{row.repName ?? "Unknown rep"}</div>
                    <div className="text-xs text-muted">
                      {row.country} | {row.month}
                    </div>
                  </td>
                  <td className="px-4 py-3">{row.interventionType ?? "Unknown type"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge value={row.requestConfirmationStatus} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge value={row.postConfirmationStatus} />
                  </td>
                  <td className="px-4 py-3">
                    <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 text-xs" onClick={() => onSelect(row)}>Open</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800 p-4 text-sm">
        <span className="text-muted">
          {formatCount(total)} requests | Page {page} of {totalPages}
        </span>
        <div className="flex gap-2">
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

function WorkflowRequestDetail({ request }: { request: WorkflowRequestRow }) {
  return (
    <div className="space-y-5">
      <header className="border-b border-zinc-800 pb-4">
        <p className="text-xs font-medium uppercase tracking-wide text-accent">Workflow request</p>
        <h2 className="mt-2 break-words text-2xl font-semibold">{request.reqId ?? "No request ID"}</h2>
        <p className="mt-1 text-sm text-muted">
          {request.repName ?? "Unknown rep"} | {request.country} | {request.month}
        </p>
      </header>

      <section>
        <h3 className="font-semibold">Current blocker</h3>
        <div className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-3">
          <p className="text-xs text-muted">Owner stage</p>
          <p className="mt-1 break-words font-semibold text-zinc-100">{request.currentOwnerStage ?? "Unknown"}</p>
        </div>
      </section>

      <section>
        <h3 className="font-semibold">Evidence dates</h3>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <DetailMetric label="Expense submitted" value={request.expenseSubmittedDate ?? "Not available"} />
          <DetailMetric label="Expense confirmed" value={request.expenseConfirmedDate ?? "Not available"} />
        </div>
      </section>

      <section>
        <h3 className="font-semibold">Workflow state</h3>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <DetailMetric label="Request approval" value={request.requestApprovalStatus} />
          <DetailMetric label="Request confirmation" value={request.requestConfirmationStatus} />
          <DetailMetric label="Post approval" value={request.postApprovalStatus} />
          <DetailMetric label="Post confirmation" value={request.postConfirmationStatus} />
        </div>
      </section>

      <section>
        <h3 className="font-semibold">Intervention</h3>
        <div className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-3">
          <p className="break-words font-semibold text-zinc-100">{request.interventionType ?? "Unknown type"}</p>
          {request.scopeStatus || request.scopeReason ? (
            <p className="mt-2 text-xs leading-5 text-muted">{request.scopeReason ?? request.scopeStatus}</p>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-3">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-1 break-words font-semibold text-zinc-100">{value}</p>
    </div>
  );
}

type ExecutionKpiTone = "cyan" | "sky" | "emerald" | "amber" | "violet";

const EXECUTION_KPI_TONE_CLASSES: Record<ExecutionKpiTone, { card: string; label: string; value: string }> = {
  cyan: {
    card: "bg-[linear-gradient(135deg,rgba(103,232,249,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-cyan-200/75",
    value: "text-cyan-50",
  },
  sky: {
    card: "bg-[linear-gradient(135deg,rgba(125,211,252,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-sky-200/75",
    value: "text-sky-50",
  },
  emerald: {
    card: "bg-[linear-gradient(135deg,rgba(110,231,183,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-emerald-200/75",
    value: "text-emerald-50",
  },
  amber: {
    card: "bg-[linear-gradient(135deg,rgba(251,191,36,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-amber-200/75",
    value: "text-amber-50",
  },
  violet: {
    card: "bg-[linear-gradient(135deg,rgba(196,181,253,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-violet-200/75",
    value: "text-violet-50",
  },
};

function KpiCard({ icon, label, value, tone }: { icon: ReactNode; label: string; value: string; tone: ExecutionKpiTone }) {
  const toneClasses = EXECUTION_KPI_TONE_CLASSES[tone];
  return (
    <div className={`dashboard-card relative p-4 ${toneClasses.card}`}>
      <div className={`flex items-center gap-2 ${toneClasses.label}`}>
        {icon}
        <p className="text-sm">{label}</p>
      </div>
      <p className={`mt-3 text-2xl font-semibold ${toneClasses.value}`}>{value}</p>
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
