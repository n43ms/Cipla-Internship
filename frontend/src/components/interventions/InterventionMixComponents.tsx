import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { InterventionMixRow } from "../../types/api";
import { SortableHeader, useSortableRows } from "../common/SortableTable";

const INTERVENTION_SORT_ACCESSORS = {
  type: (row: InterventionMixRow) => `${row.interventionType} ${row.interventionSubType ?? ""}`,
  requests: (row: InterventionMixRow) => row.requestCount,
  matched: (row: InterventionMixRow) => row.matchedRequestCount,
  approved: (row: InterventionMixRow) => row.approvedCount,
  executedRequests: (row: InterventionMixRow) => row.executedRequestCount,
  executedSnapshots: (row: InterventionMixRow) => row.executedSnapshotCount,
  actionDueRequests: (row: InterventionMixRow) => row.actionDueRequestCount,
  actionDueSnapshots: (row: InterventionMixRow) => row.actionDueSnapshotCount,
  matchedWithoutExecution: (row: InterventionMixRow) => row.matchedWithoutExecutionCount,
  pendingReport: (row: InterventionMixRow) => row.reportPendingCount,
  actualSpend: (row: InterventionMixRow) => row.totalActualSpend,
  fx: (row: InterventionMixRow) => row.fxRateStatus,
};

export function InterventionMixChart({ rows }: { rows: InterventionMixRow[] }) {
  const data = rows.slice(0, 8).map((row) => ({
    name: truncate(row.interventionType, 28),
    fullName: row.interventionType,
    requests: row.requestCount,
    matched: row.matchedRequestCount,
    executedRequests: row.executedRequestCount,
    executedSnapshots: row.executedSnapshotCount,
    actionDueSnapshots: row.actionDueSnapshotCount,
    pending: row.reportPendingCount,
  }));

  return (
    <div className="dashboard-card p-4">
      <div className="mb-4">
        <h3 className="font-medium">Intervention type mix</h3>
        <p className="text-sm text-muted">Category totals separate requests, matched evidence, true executed snapshots, action-due snapshots, and pending reports.</p>
      </div>
      {data.length === 0 ? (
        <p className="text-sm text-muted">No intervention rows match the current filters.</p>
      ) : (
        <div className="chart-frame h-[34rem] sm:h-[30rem]">
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={240} debounce={100}>
            <BarChart data={data} layout="vertical" margin={{ left: 0, right: 16, top: 8, bottom: 84 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" width={106} tick={{ fontSize: 11 }} />
              <Tooltip cursor={{ fill: "rgba(97, 199, 187, 0.075)" }} labelFormatter={(_label, payload) => payload?.[0]?.payload?.fullName ?? _label} />
              <Legend wrapperStyle={{ bottom: 0, fontSize: 11, lineHeight: "18px" }} />
              <Bar dataKey="requests" fill="#68add4" radius={[0, 4, 4, 0]} animationDuration={800} />
              <Bar dataKey="matched" name="matched evidence" fill="#9b8ac7" radius={[0, 4, 4, 0]} animationDuration={800} />
              <Bar dataKey="executedRequests" name="executed request links" fill="#58baad" radius={[0, 4, 4, 0]} animationDuration={800} />
              <Bar dataKey="executedSnapshots" name="executed snapshots" fill="#75bd83" radius={[0, 4, 4, 0]} animationDuration={800} />
              <Bar dataKey="actionDueSnapshots" name="action-due snapshots" fill="#d0a85d" radius={[0, 4, 4, 0]} animationDuration={800} />
              <Bar dataKey="pending" name="pending report" fill="#c77984" radius={[0, 4, 4, 0]} animationDuration={800} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export function InterventionMixTable({ rows }: { rows: InterventionMixRow[] }) {
  const sorted = useSortableRows(rows, INTERVENTION_SORT_ACCESSORS);
  return (
    <div className="dashboard-card">
      <div className="border-b border-zinc-800 p-4">
        <h3 className="font-medium">Intervention mix</h3>
        <p className="mt-1 text-sm text-muted">Aggregated by intervention type/subtype for the selected scope.</p>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">No intervention rows match the current data.</p>
      ) : (
        <div className="table-scroll">
          <table className="w-full min-w-[1040px] text-left text-sm">
            <thead className="table-head">
              <tr>
                <SortableHeader column="type" label="Type" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="requests" label="Requests" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="matched" label="Matched" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="approved" label="Approved" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="executedRequests" label="Executed request links" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="executedSnapshots" label="Executed snapshots" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="actionDueRequests" label="Action-due request links" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="actionDueSnapshots" label="Action-due snapshots" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="matchedWithoutExecution" label="Matched without execution" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="pendingReport" label="Pending report" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="actualSpend" label="Actual spend" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="fx" label="FX" sort={sorted.sort} onSort={sorted.onSort} />
              </tr>
            </thead>
            <tbody>
              {sorted.rows.map((row) => (
                <tr key={`${row.interventionType}-${row.interventionSubType ?? "all"}`} className="table-row">
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

function truncate(value: string, length: number) {
  return value.length > length ? `${value.slice(0, length - 1)}...` : value;
}
