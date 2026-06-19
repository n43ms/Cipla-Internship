import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getBudgetSummary } from "../api/budget";
import { getFilters } from "../api/filters";
import { BudgetCards, BudgetGapTable, BudgetSpendChart, FxWarning, LocalCurrencyBreakdown } from "../components/budget/BudgetComponents";
import { DataFreshnessBanner, EmptyState, ErrorState } from "../components/common/DataStateComponents";

export function BudgetUtilization() {
  const [country, setCountry] = useState("");
  const [month, setMonth] = useState("");
  const [page, setPage] = useState(1);
  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const budget = useQuery({
    queryKey: ["budget-summary", country, month, page],
    queryFn: () => getBudgetSummary({ country, month, page, pageSize: 25 }),
  });

  if (budget.isLoading) return <main className="p-6 text-sm text-slate-500">Loading budget utilization</main>;
  if (budget.isError) return <main className="p-6"><ErrorState title="Budget utilization unavailable" /></main>;
  if (!budget.data) return null;

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">Budget governance</p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-950">Budget utilization</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Separates planned budget, confirmed contracted value, BTU direct spend, BTC overhead spend, total actual spend, FX status, and unmatched spend.
          </p>
        </header>
        <DataFreshnessBanner meta={budget.data.meta} />
        <section className="dashboard-card p-4">
          <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
            <label className="grid gap-1 text-sm">
              <span className="font-medium text-slate-700">Country</span>
              <select className="rounded-md border border-slate-300 bg-white px-3 py-2" value={country} onChange={(event) => { setCountry(event.target.value); setPage(1); }}>
                <option value="">All primary-scope countries</option>
                {filters.data?.countries?.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
              </select>
            </label>
            <label className="grid gap-1 text-sm">
              <span className="font-medium text-slate-700">Month</span>
              <select className="rounded-md border border-slate-300 bg-white px-3 py-2" value={month} onChange={(event) => { setMonth(event.target.value); setPage(1); }}>
                <option value="">All primary-scope months</option>
                {filters.data?.months?.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
              </select>
            </label>
            <button className="soft-button self-end rounded-md border border-slate-200 px-4 py-2 text-sm" onClick={() => { setCountry(""); setMonth(""); setPage(1); }}>Clear</button>
          </div>
        </section>
        <FxWarning data={budget.data} />
        <BudgetCards data={budget.data} />
        <LocalCurrencyBreakdown data={budget.data} />
        {budget.data.rows.length ? (
          <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
            <BudgetSpendChart data={budget.data} />
            <BudgetGapTable data={budget.data} page={page} onPageChange={setPage} />
          </div>
        ) : (
          <EmptyState title="No budget rows" detail="No budget data matches the current analytical scope." />
        )}
      </div>
    </main>
  );
}
