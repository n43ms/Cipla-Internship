import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { BudgetSummaryResponse } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";

export function BudgetCards({ data }: { data: BudgetSummaryResponse }) {
  return (
    <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Planned budget" value={money(data.plannedBudgetUsd, "USD")} detail="Yearly planner total cost" />
      <KpiCard label="Confirmed contracted" value={money(data.confirmedContractedAmountUsd, "USD")} detail="Confirmed amount drives governance" />
      <KpiCard label="Actual total spend" value={money(data.actualTotalSpendUsd, "USD")} detail="From consolidation actual expense" />
      <KpiCard label="Unspent gap" value={money(data.unspentGapUsd, "USD")} detail={`${data.planWithoutSpendCount} plan-only rows`} />
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
        <ResponsiveContainer width="100%" height="100%">
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

export function BudgetGapTable({ data }: { data: BudgetSummaryResponse }) {
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-200 p-4">
        <h2 className="font-semibold text-slate-950">Event budget gaps and unmatched spend</h2>
        <p className="text-sm text-slate-500">Shows plan-only gaps, spend-without-plan, FX status, and BTU/BTC reconciliation.</p>
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
                  <p className="text-xs text-slate-500">{row.country} · {row.month}</p>
                </td>
                <td className="px-4 py-3">{row.matchStatus.replaceAll("_", " ")}</td>
                <td className="px-4 py-3">{money(row.plannedBudgetUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.actualTotalExpenseUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.unspentGapUsd ?? row.overrunAmountUsd, "USD")}</td>
                <td className="px-4 py-3">{row.fxRateStatus}</td>
                <td className="px-4 py-3">{row.btuBtcReconciliationStatus.replaceAll("_", " ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
