import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { InterventionMixRow } from "../../types/api";
import { CHART_AXIS_TICK, CHART_COLORS, CHART_GRID_PROPS, CHART_TOOLTIP_CURSOR, CHART_TOOLTIP_PROPS, ChartLegendPills } from "../common/ChartTheme";
import { SortableHeader, useSortableRows } from "../common/SortableTable";
import { formatTitleText } from "../../utils/textFormat";

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
};

const INTERVENTION_SERIES = [
  { key: "requests", label: "Requests", color: CHART_COLORS.sky },
  { key: "matched", label: "Matched evidence", color: CHART_COLORS.violet },
  { key: "executedRequests", label: "Executed links", color: CHART_COLORS.cyan },
  { key: "executedSnapshots", label: "Executed snapshots", color: CHART_COLORS.emerald },
  { key: "actionDueSnapshots", label: "Action due", color: CHART_COLORS.amber },
  { key: "pending", label: "Pending report", color: CHART_COLORS.rose },
];

export function InterventionMixChart({ rows }: { rows: InterventionMixRow[] }) {
  const data = rows.slice(0, 8).map((row) => ({
    name: truncate(formatTitleText(row.interventionType), 28),
    fullName: formatTitleText(row.interventionType),
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
          <ChartLegendPills items={INTERVENTION_SERIES.map((series) => ({ label: series.label, color: series.color }))} />
        </div>
      {data.length === 0 ? (
        <p className="text-sm text-muted">No intervention rows match the current filters.</p>
      ) : (
        <div className="chart-frame h-[32rem] sm:h-[28rem]">
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={240} debounce={100}>
            <BarChart data={data} layout="vertical" margin={{ left: 2, right: 18, top: 8, bottom: 18 }} barCategoryGap="18%">
              <CartesianGrid {...CHART_GRID_PROPS} horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={CHART_AXIS_TICK} tickLine={false} axisLine={false} />
              <YAxis type="category" dataKey="name" width={112} tick={CHART_AXIS_TICK} tickLine={false} axisLine={{ stroke: "rgba(161,161,170,0.18)" }} />
              <Tooltip
                {...CHART_TOOLTIP_PROPS}
                cursor={CHART_TOOLTIP_CURSOR}
                labelFormatter={(_label, payload) => payload?.[0]?.payload?.fullName ?? _label}
              />
              {INTERVENTION_SERIES.map((series) => (
                <Bar
                  key={series.key}
                  dataKey={series.key}
                  name={series.label}
                  fill={series.color}
                  radius={[0, 5, 5, 0]}
                  maxBarSize={12}
                  animationDuration={800}
                />
              ))}
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
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-zinc-800 p-4">
        <h3 className="font-medium">Intervention mix</h3>
        <p className="mt-1 text-sm text-muted">Aggregated by intervention type/subtype for the selected scope.</p>
      </div>
      {rows.length === 0 ? (
        <p className="p-4 text-sm text-muted">No intervention rows match the current data.</p>
      ) : (
        <div className="overflow-hidden">
          <table className="w-full table-fixed text-left text-xs lg:text-sm">
            <thead className="table-head">
              <tr>
                <SortableHeader column="type" label="Type" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="requests" label="Requests" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="matched" label="Matched" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="approved" label="Approved" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="executedRequests" label="Executed" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="actionDueRequests" label="Action due" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="pendingReport" label="Pending" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="actualSpend" label="Spend" sort={sorted.sort} onSort={sorted.onSort} />
              </tr>
            </thead>
            <tbody>
              {sorted.rows.map((row) => (
                <tr key={`${row.interventionType}-${row.interventionSubType ?? "all"}`} className="table-row">
                  <td className="px-3 py-3 align-top">
                    <div className="truncate font-medium" title={formatTitleText(row.interventionType)}>{formatTitleText(row.interventionType)}</div>
                    <div className="truncate text-xs text-muted" title={formatTitleText(row.interventionSubType, "All subtypes")}>{formatTitleText(row.interventionSubType, "All subtypes")}</div>
                  </td>
                  <td className="px-3 py-3 align-top">{formatCount(row.requestCount)}</td>
                  <td className="px-3 py-3 align-top">{formatCount(row.matchedRequestCount)}</td>
                  <td className="px-3 py-3 align-top">{formatCount(row.approvedCount)}</td>
                  <td className="px-3 py-3 align-top">
                    <StackedCount primary={row.executedRequestCount} secondary={row.executedSnapshotCount} secondaryLabel="snap" />
                  </td>
                  <td className="px-3 py-3 align-top">
                    <StackedCount primary={row.actionDueRequestCount} secondary={row.actionDueSnapshotCount} secondaryLabel="snap" />
                  </td>
                  <td className="px-3 py-3 align-top">
                    {formatCount(row.reportPendingCount)}
                  </td>
                  <td className="px-3 py-3 align-top">{formatAmount(row.totalActualSpend)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function StackedCount({ primary, secondary, secondaryLabel }: { primary: number; secondary: number; secondaryLabel: string }) {
  return (
    <div>
      <div>{formatCount(primary)}</div>
      <div className="truncate text-[0.68rem] text-muted" title={`${formatCount(secondary)} ${secondaryLabel}`}>
        {formatCount(secondary)} {secondaryLabel}
      </div>
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
