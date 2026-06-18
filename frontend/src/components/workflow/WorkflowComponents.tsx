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
    <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

export function WorkflowStatusTable({ counts, title }: { counts: Record<string, number>; title: string }) {
  const entries = Object.entries(counts);
  return (
    <div className="dashboard-card p-4">
      <h3 className="font-medium">{title}</h3>
      <div className="mt-3 space-y-2">
        {entries.length === 0 ? <p className="text-sm text-muted">No workflow rows.</p> : null}
        {entries.map(([status, count]) => (
          <div key={status} className="flex min-w-0 items-center justify-between gap-3 text-sm">
            <StatusBadge value={status} />
            <span className="font-medium">{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
