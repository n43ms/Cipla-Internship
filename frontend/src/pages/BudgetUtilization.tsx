import { useQuery } from "@tanstack/react-query";

import { getBudgetSummary } from "../api/budget";
import { BudgetCards, BudgetGapTable, BudgetSpendChart, FxWarning } from "../components/budget/BudgetComponents";
import { DataFreshnessBanner, EmptyState, ErrorState } from "../components/common/DataStateComponents";

export function BudgetUtilization() {
  const budget = useQuery({ queryKey: ["budget-summary"], queryFn: () => getBudgetSummary() });

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
        <FxWarning data={budget.data} />
        <BudgetCards data={budget.data} />
        {budget.data.rows.length ? (
          <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
            <BudgetSpendChart data={budget.data} />
            <BudgetGapTable data={budget.data} />
          </div>
        ) : (
          <EmptyState title="No budget rows" detail="No budget data matches the current analytical scope." />
        )}
      </div>
    </main>
  );
}
