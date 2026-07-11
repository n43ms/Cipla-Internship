import { AlertTriangle } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { BudgetSummaryResponse, LocalCurrencyTotal } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";
import { TableLoadingOverlay } from "../common/TableLoadingOverlay";
import { SortableHeader, type SortState, useSortableRows } from "../common/SortableTable";
import { WarningRegistration } from "../common/WarningCenter";

const LOCAL_CURRENCY_SORT_ACCESSORS = {
  currency: (row: LocalCurrencyTotal) => row.currencyCode,
  confirmed: (row: LocalCurrencyTotal) => row.confirmedContractedAmountLocal,
  btu: (row: LocalCurrencyTotal) => row.directHcpBtuSpendLocal,
  btc: (row: LocalCurrencyTotal) => row.overheadBtcSpendLocal,
  actual: (row: LocalCurrencyTotal) => row.actualTotalSpendLocal,
  rows: (row: LocalCurrencyTotal) => row.rowCount,
};

export type BudgetGapSortKey = "eventName" | "matchStatus" | "plannedBudgetUsd" | "actualSpendUsd" | "unspentGapUsd";

export function BudgetCards({ data }: { data: BudgetSummaryResponse }) {
  return (
    <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Planned budget" value={money(data.plannedBudgetUsd, "USD")} detail="Yearly planner total cost" />
      <KpiCard label="Confirmed contracted" value={money(data.confirmedContractedAmountUsd, "USD")} detail="Confirmed amount drives governance" />
      <KpiCard label="Actual total spend" value={money(data.actualTotalSpendUsd, "USD")} detail="From consolidation actual expense" />
      <KpiCard label="Unspent gap" value={money(data.unspentGapUsd, "USD")} detail={`${data.planWithoutSpendCount} plan-only rows, grouped by plan event`} />
    </div>
  );
}

export function LocalCurrencyBreakdown({ data }: { data: BudgetSummaryResponse }) {
  if (!data.localTotalsByCurrency.length) return null;
  return <LocalCurrencyTable data={data} />;
}

function LocalCurrencyTable({ data }: { data: BudgetSummaryResponse }) {
  const sorted = useSortableRows(data.localTotalsByCurrency, LOCAL_CURRENCY_SORT_ACCESSORS);
  const showBtuColumn = hasMeaningfulBtuSplit(data);
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold text-zinc-50">Local currency totals</h2>
        <p className="text-sm text-zinc-500">Local money is grouped by currency. Direct-spend split is shown only when the source provides it.</p>
      </div>
      <div className="table-scroll">
        <table className="min-w-full text-left text-sm">
          <thead className="table-head">
            <tr>
              <SortableHeader column="currency" label="Currency" sort={sorted.sort} onSort={sorted.onSort} />
              <SortableHeader column="confirmed" label="Confirmed" sort={sorted.sort} onSort={sorted.onSort} />
              {showBtuColumn ? <SortableHeader column="btu" label="Direct spend" sort={sorted.sort} onSort={sorted.onSort} /> : null}
              <SortableHeader column="btc" label="BTC" sort={sorted.sort} onSort={sorted.onSort} />
              <SortableHeader column="actual" label="Actual" sort={sorted.sort} onSort={sorted.onSort} />
              <SortableHeader column="rows" label="Rows" sort={sorted.sort} onSort={sorted.onSort} />
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {sorted.rows.map((row) => (
              <tr key={row.currencyCode} className="transition-colors duration-150 hover:bg-zinc-800/45">
                <td className="px-4 py-3 font-medium">{row.currencyCode}</td>
                <td className="px-4 py-3">{money(row.confirmedContractedAmountLocal, row.currencyCode)}</td>
                {showBtuColumn ? <td className="px-4 py-3">{localBtuCell(row)}</td> : null}
                <td className="px-4 py-3">{money(row.overheadBtcSpendLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{money(row.actualTotalSpendLocal, row.currencyCode)}</td>
                <td className="px-4 py-3">{row.rowCount}</td>
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
    { label: "BTC", amount: data.overheadBtcSpendUsd },
  ];
  if (hasMeaningfulBtuSplit(data)) {
    rows.splice(3, 0, { label: "Direct", amount: data.directHcpBtuSpendUsd });
  }
  return (
    <div className="dashboard-card p-4">
      <h2 className="font-semibold text-zinc-50">Spend split</h2>
      <div className="chart-frame mt-3 h-80">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={240} debounce={100}>
          <BarChart data={rows} margin={{ top: 12, right: 20, left: 8, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis width={70} tickFormatter={(value) => compact(value as number)} />
            <Tooltip cursor={{ fill: "rgba(97, 199, 187, 0.075)" }} formatter={(value) => money(Number(value), "USD")} />
            <Legend />
            <Bar dataKey="amount" name="USD amount" fill="#64c8bc" radius={[4, 4, 0, 0]} animationDuration={800} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function BudgetGapTable({
  data,
  page,
  sort,
  isFetching = false,
  onPageChange,
  onSort,
}: {
  data: BudgetSummaryResponse;
  page: number;
  sort: SortState<BudgetGapSortKey>;
  isFetching?: boolean;
  onPageChange: (page: number) => void;
  onSort: (column: BudgetGapSortKey) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(data.total / data.pageSize));
  return (
    <div className="dashboard-card relative overflow-hidden">
      <TableLoadingOverlay isFetching={isFetching} label="Refreshing budget rows" />
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold text-zinc-50">Event budget gaps and unmatched spend</h2>
        <p className="text-sm text-zinc-500">Showing {data.rows.length} of {data.total} rows. Matched gaps are grouped by plan event in summary totals.</p>
      </div>
      <div className="table-scroll">
        <table className="min-w-full text-left text-sm">
          <thead className="table-head">
            <tr>
              <SortableHeader column="eventName" label="Event" sort={sort} onSort={onSort} />
              <SortableHeader column="matchStatus" label="Status" sort={sort} onSort={onSort} />
              <SortableHeader column="plannedBudgetUsd" label="Planned USD" sort={sort} onSort={onSort} />
              <SortableHeader column="actualSpendUsd" label="Actual USD" sort={sort} onSort={onSort} />
              <SortableHeader column="unspentGapUsd" label="Gap" sort={sort} onSort={onSort} />
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {data.rows.map((row, index) => (
              <tr key={`${row.eventName}-${index}`} className="transition-colors duration-150 hover:bg-zinc-800/45">
                <td className="max-w-[18rem] px-4 py-3">
                  <p className="truncate font-medium text-zinc-100">{row.eventName ?? "Unlabeled activity"}</p>
                  <p className="text-xs text-zinc-500">{row.country} - {row.month}</p>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap items-start gap-2">
                    <span>{row.matchStatus.replaceAll("_", " ")}</span>
                    <ExpenseSplitFlag status={row.btuBtcReconciliationStatus} />
                  </div>
                </td>
                <td className="px-4 py-3">{money(row.plannedBudgetUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.actualTotalExpenseUsd, "USD")}</td>
                <td className="px-4 py-3">{money(row.unspentGapUsd ?? row.overrunAmountUsd, "USD")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800 p-4 text-sm">
        <span className="text-zinc-500">Page {page} of {totalPages}</span>
        <div className="flex gap-2">
          <button className="soft-button rounded-md  px-3 py-1 disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
          <button className="soft-button rounded-md  px-3 py-1 disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

export function BudgetQualityNotice({ data }: { data: BudgetSummaryResponse }) {
  const items = [
    data.btuBtcReconciliationIssueCount ? `${data.btuBtcReconciliationIssueCount} rows have source expense split reconciliation issues.` : "",
  ].filter(Boolean);
  if (!items.length) return null;
  return (
    <WarningRegistration
      record={{
        id: "budget-quality",
        title: "Budget quality notes",
        detail: "Expense split checks",
        tone: "warning",
        items,
      }}
    />
  );
}

export function money(value: number | null | undefined, currency = "") {
  if (value === null || value === undefined) return "-";
  return `${currency ? `${currency} ` : ""}${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

function compact(value: number) {
  return Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function hasMeaningfulBtuSplit(data: BudgetSummaryResponse) {
  return (
    Number(data.directHcpBtuSpendUsd || 0) > 0 ||
    data.localTotalsByCurrency.some((row) => Number(row.directHcpBtuSpendLocal || 0) > 0) ||
    data.rows.some((row) => Number(row.directHcpBtuSpendLocal || 0) > 0)
  );
}

function localBtuCell(row: LocalCurrencyTotal) {
  if (Number(row.directHcpBtuSpendLocal || 0) === 0 && Number(row.actualTotalSpendLocal || 0) > 0) {
    return <span className="text-zinc-500">Not provided</span>;
  }
  return money(row.directHcpBtuSpendLocal, row.currencyCode);
}

function ExpenseSplitFlag({ status }: { status: string }) {
  const issue = expenseSplitIssue(status);
  if (!issue) return null;
  return (
    <details className="group max-w-[15rem]">
      <summary
        className={`inline-flex cursor-pointer list-none items-center gap-1 rounded-full border px-2 py-0.5 text-xs transition-colors duration-150 marker:hidden ${issue.badgeClass}`}
        aria-label={`Show expense split note: ${issue.label}`}
      >
        <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />
        <span>{issue.label}</span>
      </summary>
      <div className="mt-2 rounded-md border border-zinc-800 bg-zinc-950 p-2 text-xs leading-5 text-zinc-300 shadow-xl">
        {issue.detail}
      </div>
    </details>
  );
}

function expenseSplitIssue(status: string) {
  if (status === "reconciled") return null;
  if (status === "missing_total_actual") {
    return {
      label: "Missing total",
      detail: "Total actual spend is missing, so the row cannot be reconciled against the direct and overhead split.",
      badgeClass: "border-zinc-700 bg-zinc-800/55 text-zinc-300 hover:bg-zinc-800",
    };
  }
  if (status === "missing_btu_btc_split") {
    return {
      label: "Split missing",
      detail: "The source did not provide direct and overhead spend split fields for this row.",
      badgeClass: "border-zinc-700 bg-zinc-800/55 text-zinc-300 hover:bg-zinc-800",
    };
  }
  if (status === "mismatch") {
    return {
      label: "Review split",
      detail: "Direct spend plus overhead does not match total actual spend in the source row.",
      badgeClass: "border-amber-300/25 bg-amber-300/10 text-amber-100 hover:bg-amber-300/15",
    };
  }
  return {
    label: "Review",
    detail: status.replaceAll("_", " "),
    badgeClass: "border-amber-300/25 bg-amber-300/10 text-amber-100 hover:bg-amber-300/15",
  };
}
