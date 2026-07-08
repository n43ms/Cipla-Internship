import { Scatter, ScatterChart, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts";

import type { DoctorRoiResponse, DoctorRoiRow } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";
import { money } from "../budget/BudgetComponents";
import { TableLoadingOverlay } from "../common/TableLoadingOverlay";
import { SortableHeader, type SortState } from "../common/SortableTable";

export type DoctorRoiSortKey = "doctorName" | "roiSegment" | "quadrantLabel" | "engagementCount" | "rcpaLastMonth" | "totalRoiSpendUsd" | "ciplaPrescriptionQty";

export function DoctorRoiCards({ data }: { data: DoctorRoiResponse }) {
  const darkHorse = data.rows.filter((row) => row.darkHorseFlag).length;
  const noRcpa = data.rows.filter((row) => !row.hasRcpa).length;
  return (
    <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Doctor ROI rows" value={data.total} detail="Country-scoped Pcode universe" />
      <KpiCard label="Dark-horse rows" value={darkHorse} detail="Unengaged low effort / high reward" />
      <KpiCard label="No RCPA rows" value={noRcpa} detail="Engagement exists without prescription coverage" />
      <KpiCard label="Segments" value={Object.keys(data.segmentCounts).length} detail="Deterministic ROI buckets" />
    </div>
  );
}

export function DoctorScatter({ rows }: { rows: DoctorRoiRow[] }) {
  return (
    <div className="dashboard-card p-4">
      <h2 className="font-semibold text-zinc-50">Spend vs Cipla prescriptions</h2>
      <div className="chart-frame mt-3 h-96">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={280} debounce={100}>
          <ScatterChart margin={{ top: 16, right: 24, bottom: 28, left: 12 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="quadrantX" name="Spend" tickFormatter={(value) => compact(value as number)} />
            <YAxis dataKey="quadrantY" name="Cipla Rx" tickFormatter={(value) => compact(value as number)} width={72} />
            <Tooltip
              cursor={{ stroke: "#61c7bb", strokeOpacity: 0.28, strokeDasharray: "3 3" }}
              formatter={(value, name) => [Number(value).toLocaleString(), name]}
              labelFormatter={(_, payload) => payload?.[0]?.payload?.doctorName ?? "Doctor"}
            />
            <Legend />
            <Scatter name="Doctors" data={rows} fill="#62c4b8" animationDuration={800} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function QuadrantMatrix({ counts }: { counts: Record<string, number> }) {
  const labels = ["low effort / high reward", "high effort / high reward", "low effort / low reward", "high effort / low reward", "insufficient data"];
  return (
    <div className="dashboard-card p-4">
      <h2 className="font-semibold text-zinc-50">ROI quadrant matrix</h2>
      <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {labels.map((label) => (
          <div key={label} className="rounded-lg border border-zinc-800 bg-zinc-950/70 p-3">
            <p className="text-sm font-semibold capitalize text-zinc-200">{label}</p>
            <p className="mt-2 text-2xl font-semibold">{counts[label] ?? 0}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function DoctorRoiTable({
  rows,
  page,
  pageSize,
  total,
  sort,
  isFetching = false,
  onPageChange,
  onSelect,
  onSort,
}: {
  rows: DoctorRoiRow[];
  page: number;
  pageSize: number;
  total: number;
  sort: SortState<DoctorRoiSortKey>;
  isFetching?: boolean;
  onPageChange: (page: number) => void;
  onSelect: (row: DoctorRoiRow) => void;
  onSort: (column: DoctorRoiSortKey) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return (
    <div className="dashboard-card relative overflow-hidden">
      <TableLoadingOverlay isFetching={isFetching} label="Refreshing doctor rows" />
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold text-zinc-50">Doctor opportunities</h2>
        <p className="text-sm text-zinc-500">Showing {rows.length} of {total} rows. Sorted by dark-horse flag, prescription volume, and spend.</p>
      </div>
      <div className="table-scroll">
        <table className="min-w-full text-left text-sm">
          <thead className="table-head">
            <tr>
              <SortableHeader column="doctorName" label="Doctor" sort={sort} onSort={onSort} />
              <SortableHeader column="roiSegment" label="Segment" sort={sort} onSort={onSort} />
              <SortableHeader column="quadrantLabel" label="Quadrant" sort={sort} onSort={onSort} />
              <SortableHeader column="engagementCount" label="Engagements" sort={sort} onSort={onSort} />
              <SortableHeader column="rcpaLastMonth" label="RCPA baseline" sort={sort} onSort={onSort} />
              <SortableHeader column="totalRoiSpendUsd" label="Spend" sort={sort} onSort={onSort} />
              <SortableHeader column="ciplaPrescriptionQty" label="Cipla Rx" sort={sort} onSort={onSort} />
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {rows.map((row) => (
              <tr key={`${row.countryCode}-${row.pcodeNormalized}`}>
                <td className="max-w-[16rem] px-4 py-3">
                  <p className="truncate font-medium text-zinc-100">{row.doctorName ?? "Unknown doctor"}</p>
                  <p className="text-xs text-zinc-500">{row.countryCode} - {row.pcodeNormalized}</p>
                </td>
                <td className="px-4 py-3">
                  {row.roiSegment.replaceAll("_", " ")}
                  {row.darkHorseUnengagedFlag ? <span className="ml-2 rounded-full bg-emerald-400/10 px-2 py-1 text-xs text-emerald-300">unengaged opportunity</span> : null}
                  {row.highValueEngagedFlag ? <span className="ml-2 rounded-full bg-cyan-400/10 px-2 py-1 text-xs text-cyan-300">engaged value</span> : null}
                  {!row.hasRcpa ? <span className="ml-2 rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">no RCPA</span> : null}
                </td>
                <td className="px-4 py-3">{row.quadrantLabel}</td>
                <td className="px-4 py-3">{row.engagementCount}</td>
                <td className="px-4 py-3 text-xs text-zinc-400">{rcpaPeriod(row)}</td>
                <td className="px-4 py-3">{money(row.totalRoiSpendUsd, "USD")}</td>
                <td className="px-4 py-3">{row.ciplaPrescriptionQty.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 text-xs" onClick={() => onSelect(row)}>Open</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800 p-4 text-sm">
        <span className="text-zinc-500">Page {page} of {totalPages}</span>
        <div className="flex gap-2">
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

function compact(value: number) {
  return Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function rcpaPeriod(row: DoctorRoiRow) {
  if (!row.hasRcpa) return "No RCPA baseline";
  if (!row.rcpaFirstMonth || !row.rcpaLastMonth) return "Baseline period unknown";
  return `${formatMonth(row.rcpaFirstMonth)} to ${formatMonth(row.rcpaLastMonth)}`;
}

function formatMonth(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: "short", year: "numeric" });
}
