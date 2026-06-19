import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { BudgetSummaryResponse } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";

export function BudgetCards({ data }: { data: BudgetSummaryResponse }) {
  return (
    <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Planned budget" value={money(data.plannedBudgetUsd, "USD")} detail="Yearly planner total cost" />
      <KpiCard label="Confirmed contracted" value={money(data.confirmedContractedAmountUsd, "USD")} detail="Confirmed amount drives governance" />
      <KpiCard label="Actual total spend" value={money(data.actualTotalSpendUsd, "USD")} detail="From consolidation actual expense" />
      <KpiCard label="Unspent gap" value={money(data.unspentGapUsd, "USD")} detail={`${data.planWithoutSpendCount} plan-only rows, grouped by plan event`} />
    </div>
  );
}

export function LocalCurrencyBreakdown({ data }: { data: BudgetSummaryResponse }) {
  if (!data.localTotalsByCurrency.length) return null;
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-200 p-4">
        <h2 className="font-semibold text-slate-950">Local currency totals</h2>
        <p className="text-sm text-slate-500">Local money is grouped by currency. Missing-FX currencies are not silently mixed into USD comparisons.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Currency</th>
              <th className="px-4 py-3">Confirmed</th>
              <th className="px-4 py-3">BTU</th>
              <th className="px-4 py-3">BTC</th>
              <th className="px-4 py-3">Actual</th>
              <th className="px-4 py-3">Rows</th>
              <th className="px-4 py-3">FX quality</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.localTotalsByCurrency.map((row) => (
              <tr key={row.currencyCode}>
                <td className="px-4 py-3 font-medium">{row.currencyCode}</td>
                <td className="px-4 py-3">{money(row.confirmedContractedAmountLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{money(row.directHcpBtuSpendLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{money(row.overheadBtcSpendLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{money(row.actualTotalSpendLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{row.rowCount}</td>
                <td className="px-4 py-3">{row.missingFxCount ? `${row.missingFxCount} missing FX` : row.provisionalFxCount ? `${row.provisionalFxCount} provisional` : "official/normalized"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function BudgetSpendChart({ data }: { data: BudgetSummaryResponse }) {
  const rows = [
    { label: "Planned", amount: data.plannedBudgetUsd },
    { label: "Confirmed", amount: data.confirmedContractedAmountUsd },
    { label: "Actual", amount: data.actualTotalSpendUsd },
    { label: "BTU", amount: data.directHcpBtuSpendUsd },
    { label: "BTC", amount: data.overheadBtcSpendUsd },
  ];
  return (
    <div className="dashboard-card p-4">
      <h2 className="font-semibold text-slate-950">Budget split</h2>
      <div className="chart-frame mt-3 h-80">
        <ResponsiveContainer width="100%" height="100%" minWidth={320} minHeight={240}>
          <BarChart data={rows} margin={{ top: 12, right: 20, left: 8, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis width={70} tickFormatter={(value) => compact(value as number)} />
            <Tooltip formatter={(value) => money(Number(value), "USD")} />
            <Legend />
            <Bar dataKey="amount" name="USD amount" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function BudgetGapTable({ data, page, onPageChange }: { data: BudgetSummaryResponse; page: number; onPageChange: (page: number) => void }) {
  const totalPages = Math.max(1, Math.ceil(data.total / data.pageSize));
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-200 p-4">
        <h2 className="font-semibold text-slate-950">Event budget gaps and unmatched spend</h2>
        <p className="text-sm text-slate-500">Showing {data.rows.length} of {data.total} rows. Matched gaps are grouped by plan event in summary totals.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Event</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Planned USD</th>
              <th className="px-4 py-3">Actual USD</th>
              <th className="px-4 py-3">Gap</th>
              <th className="px-4 py-3">FX</th>
              <th className="px-4 py-3">BTU/BTC</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.rows.map((row, index) => (
              <tr key={`${row.eventName}-${index}`}>
                <td className="max-w-[18rem] px-4 py-3">
                  <p className="truncate font-medium text-slate-900">{row.eventName ?? "Unlabeled activity"}</p>
                  <p className="text-xs text-slate-500">{row.country} - {row.month}</p>
                </td>
                <td className="px-4 py-3">{row.matchStatus.replaceAll("_", " ")}</td>
                <td className="px-4 py-3">{money(row.plannedBudgetUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.actualTotalExpenseUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.unspentGapUsd ?? row.overrunAmountUsd, "USD")}</td>
                <td className="px-4 py-3"><span className={row.fxRateStatus === "missing" ? "rounded-full bg-amber-100 px-2 py-1 text-xs text-amber-800" : ""}>{row.fxRateStatus}</span></td>
                <td className="px-4 py-3"><span className={row.btuBtcReconciliationStatus === "mismatch" ? "rounded-full bg-red-100 px-2 py-1 text-xs text-red-800" : ""}>{row.btuBtcReconciliationStatus.replaceAll("_", " ")}</span></td>
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

export function FxWarning({ data }: { data: BudgetSummaryResponse }) {
  if (!data.missingFxCount && !data.provisionalFxCount && !data.btuBtcReconciliationIssueCount) return null;
  return (
    <div className="dashboard-card border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
      {data.missingFxCount ? <p>{data.missingFxCount} rows have missing company FX and remain local-currency only.</p> : null}
      {data.provisionalFxCount ? <p>{data.provisionalFxCount} rows use provisional FX.</p> : null}
      {data.btuBtcReconciliationIssueCount ? <p>{data.btuBtcReconciliationIssueCount} rows have BTU/BTC reconciliation issues.</p> : null}
    </div>
  );
}

export function money(value: number | null | undefined, currency = "") {
  if (value === null || value === undefined) return "-";
  return `${currency ? `${currency} ` : ""}${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

function compact(value: number) {
  return Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}
