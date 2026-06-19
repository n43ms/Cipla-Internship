import { Scatter, ScatterChart, ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts";

import type { DoctorRoiResponse, DoctorRoiRow } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";
import { money } from "../budget/BudgetComponents";

export function DoctorRoiCards({ data }: { data: DoctorRoiResponse }) {
  const darkHorse = data.rows.filter((row) => row.darkHorseFlag).length;
  const noRcpa = data.rows.filter((row) => !row.hasRcpa).length;
  return (
    <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
      <h2 className="font-semibold text-slate-950">Spend vs Cipla prescriptions</h2>
      <div className="chart-frame mt-3 h-96">
        <ResponsiveContainer width="100%" height="100%" minWidth={320} minHeight={280}>
          <ScatterChart margin={{ top: 16, right: 24, bottom: 28, left: 12 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="quadrantX" name="Spend" tickFormatter={(value) => compact(value as number)} />
            <YAxis dataKey="quadrantY" name="Cipla Rx" tickFormatter={(value) => compact(value as number)} width={72} />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              formatter={(value, name) => [Number(value).toLocaleString(), name]}
              labelFormatter={(_, payload) => payload?.[0]?.payload?.doctorName ?? "Doctor"}
            />
            <Legend />
            <Scatter name="Doctors" data={rows} fill="#2563eb" />
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
      <h2 className="font-semibold text-slate-950">ROI quadrant matrix</h2>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {labels.map((label) => (
          <div key={label} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
            <p className="text-sm font-semibold capitalize text-slate-800">{label}</p>
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
  onPageChange,
  onSelect,
}: {
  rows: DoctorRoiRow[];
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onSelect: (row: DoctorRoiRow) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-200 p-4">
        <h2 className="font-semibold text-slate-950">Doctor opportunities</h2>
        <p className="text-sm text-slate-500">Showing {rows.length} of {total} rows. Sorted by dark-horse flag, prescription volume, and spend.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Doctor</th>
              <th className="px-4 py-3">Segment</th>
              <th className="px-4 py-3">Quadrant</th>
              <th className="px-4 py-3">Engagements</th>
              <th className="px-4 py-3">RCPA baseline</th>
              <th className="px-4 py-3">Spend</th>
              <th className="px-4 py-3">Cipla Rx</th>
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((row) => (
              <tr key={`${row.countryCode}-${row.pcodeNormalized}`}>
                <td className="max-w-[16rem] px-4 py-3">
                  <p className="truncate font-medium text-slate-900">{row.doctorName ?? "Unknown doctor"}</p>
                  <p className="text-xs text-slate-500">{row.countryCode} - {row.pcodeNormalized}</p>
                </td>
                <td className="px-4 py-3">
                  {row.roiSegment.replaceAll("_", " ")}
                  {row.darkHorseUnengagedFlag ? <span className="ml-2 rounded-full bg-emerald-100 px-2 py-1 text-xs text-emerald-800">unengaged opportunity</span> : null}
                  {row.highValueEngagedFlag ? <span className="ml-2 rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800">engaged value</span> : null}
                  {!row.hasRcpa ? <span className="ml-2 rounded-full bg-amber-100 px-2 py-1 text-xs text-amber-800">no RCPA</span> : null}
                </td>
                <td className="px-4 py-3">{row.quadrantLabel}</td>
                <td className="px-4 py-3">{row.engagementCount}</td>
                <td className="px-4 py-3 text-xs text-slate-600">{rcpaPeriod(row)}</td>
                <td className="px-4 py-3">{money(row.totalRoiSpendUsd, "USD")}</td>
                <td className="px-4 py-3">{row.ciplaPrescriptionQty.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <button className="soft-button rounded-md border border-slate-200 px-3 py-1 text-xs" onClick={() => onSelect(row)}>Open</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between border-t border-slate-200 p-4 text-sm">
        <span className="text-slate-500">Page {page} of {totalPages}</span>
        <div className="flex gap-2">
          <button className="soft-button rounded-md border border-slate-200 px-3 py-1 disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
          <button className="soft-button rounded-md border border-slate-200 px-3 py-1 disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
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
