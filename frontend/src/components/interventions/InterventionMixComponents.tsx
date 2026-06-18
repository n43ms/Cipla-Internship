import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { InterventionMixRow } from "../../types/api";

export function InterventionMixChart({ rows }: { rows: InterventionMixRow[] }) {
  const data = rows.slice(0, 8).map((row) => ({
    name: row.interventionType,
    requests: row.requestCount,
    matched: row.matchedRequestCount,
    executedRequests: row.executedRequestCount,
    executedSnapshots: row.executedSnapshotCount,
    actionDueSnapshots: row.actionDueSnapshotCount,
    pending: row.reportPendingCount,
  }));

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="mb-4">
        <h3 className="font-medium">Intervention type mix</h3>
        <p className="text-sm text-muted">Category totals separate requests, matched evidence, true executed snapshots, action-due snapshots, and pending reports.</p>
      </div>
      {data.length === 0 ? (
        <p className="text-sm text-muted">No intervention rows match the current filters.</p>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 126, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" width={126} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="requests" fill="#2563eb" radius={[0, 4, 4, 0]} />
              <Bar dataKey="matched" name="matched evidence" fill="#7c3aed" radius={[0, 4, 4, 0]} />
              <Bar dataKey="executedRequests" name="executed request links" fill="#0f766e" radius={[0, 4, 4, 0]} />
              <Bar dataKey="executedSnapshots" name="executed snapshots" fill="#16a34a" radius={[0, 4, 4, 0]} />
              <Bar dataKey="actionDueSnapshots" name="action-due snapshots" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              <Bar dataKey="pending" name="pending report" fill="#dc2626" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export function InterventionMixTable({ rows }: { rows: InterventionMixRow[] }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-4">
        <h3 className="font-medium">Intervention mix</h3>
        <p className="mt-1 text-sm text-muted">Aggregated by intervention type/subtype for the selected scope.</p>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">No intervention rows match the current data.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1040px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Requests</th>
                <th className="px-4 py-3">Matched</th>
                <th className="px-4 py-3">Approved</th>
                <th className="px-4 py-3">Executed request links</th>
                <th className="px-4 py-3">Executed snapshots</th>
                <th className="px-4 py-3">Action-due request links</th>
                <th className="px-4 py-3">Action-due snapshots</th>
                <th className="px-4 py-3">Matched without execution</th>
                <th className="px-4 py-3">Pending report</th>
                <th className="px-4 py-3">Actual spend</th>
                <th className="px-4 py-3">FX</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${row.interventionType}-${row.interventionSubType ?? "all"}`} className="border-t border-slate-100">
                  <td className="px-4 py-3">
                    <div className="font-medium">{row.interventionType}</div>
                    <div className="text-xs text-muted">{row.interventionSubType ?? "All subtypes"}</div>
                  </td>
                  <td className="px-4 py-3">{formatCount(row.requestCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.matchedRequestCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.approvedCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.executedRequestCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.executedSnapshotCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.actionDueRequestCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.actionDueSnapshotCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.matchedWithoutExecutionCount)}</td>
                  <td className="px-4 py-3">{formatCount(row.reportPendingCount)}</td>
                  <td className="px-4 py-3">{formatAmount(row.totalActualSpend)}</td>
                  <td className="px-4 py-3">{row.fxRateStatus}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function formatCount(value: number) {
  return new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(value);
}

function formatAmount(value: number | null) {
  if (value === null) {
    return "-";
  }
  return new Intl.NumberFormat("en", { maximumFractionDigits: 0 }).format(value);
}
