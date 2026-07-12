import { StatusBadge } from "../execution/ExecutionBadges";

export function WorkflowGovernanceCards({
  pendingRequests,
  pendingReports,
  reportsApproved,
  reportsSentForCorrection = 0,
}: {
  pendingRequests: number;
  pendingReports: number;
  reportsApproved: number;
  reportsSentForCorrection?: number;
}) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <WorkflowCard label="Pending requests" value={pendingRequests} />
      <WorkflowCard label="Pending reports" value={pendingReports} />
      <WorkflowCard label="Reports approved" value={reportsApproved} />
      <WorkflowCard label="Reports correction" value={reportsSentForCorrection} />
    </div>
  );
}

function WorkflowCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="dashboard-card p-4">
      <p className="text-xs uppercase tracking-wide text-cyan-200/75">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

export function WorkflowStatusTable({
  counts,
  maxEntries,
  title,
}: {
  counts: Record<string, number>;
  maxEntries?: number;
  title: string;
}) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const visibleEntries = maxEntries ? entries.slice(0, maxEntries) : entries;
  const hiddenCount = Math.max(entries.length - visibleEntries.length, 0);
  return (
    <div className="dashboard-card p-4">
      <h3 className="font-medium">{title}</h3>
      <div className="mt-3 space-y-2">
        {entries.length === 0 ? <p className="text-sm text-muted">No workflow rows.</p> : null}
        {visibleEntries.map(([status, count]) => (
          <div key={status} className="flex min-w-0 items-center justify-between gap-3 text-sm">
            <StatusBadge value={status} />
            <span className="font-medium">{count}</span>
          </div>
        ))}
        {hiddenCount > 0 ? (
          <p className="pt-1 text-xs text-muted">
            {hiddenCount} lower-volume {hiddenCount === 1 ? "status" : "statuses"} hidden
          </p>
        ) : null}
      </div>
    </div>
  );
}
