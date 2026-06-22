import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getBudgetSummary } from "../api/budget";
import { getFilters } from "../api/filters";
import { BudgetCards, BudgetGapTable, BudgetSpendChart, FxWarning, LocalCurrencyBreakdown, type BudgetGapSortKey } from "../components/budget/BudgetComponents";
import { DataFreshnessBanner, EmptyState, ErrorState, LoadingState } from "../components/common/DataStateComponents";
import { SmoothSelect } from "../components/common/SmoothSelect";
import { nextSort, type SortState } from "../components/common/SortableTable";

export function BudgetUtilization() {
  const [country, setCountry] = useState("");
  const [month, setMonth] = useState("");
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<SortState<BudgetGapSortKey>>({ key: "unspentGapUsd", direction: "desc" });
  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const budget = useQuery({
    queryKey: ["budget-summary", country, month, page, sort],
    queryFn: () => getBudgetSummary({ country, month, page, pageSize: 25, sort: sort.key, sortDirection: sort.direction }),
  });

  if (budget.isLoading) return <main><LoadingState label="Loading budget utilization" /></main>;
  if (budget.isError) return <main className="p-6"><ErrorState title="Budget utilization unavailable" /></main>;
  if (!budget.data) return null;

  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Budget governance</p>
          <h1 className="page-title">Budget utilization</h1>
          <p className="page-copy">
            Separates planned budget, confirmed contracted value, BTU direct spend, BTC overhead spend, total actual spend, FX status, and unmatched spend.
          </p>
        </header>
        <DataFreshnessBanner meta={budget.data.meta} />
        <section className="dashboard-card overflow-visible p-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto]">
            <div className="grid gap-1 text-sm">
              <span className="font-medium text-zinc-300">Country</span>
              <SmoothSelect ariaLabel="Country" value={country} options={filters.data?.countries ?? []} placeholder="All primary-scope countries" onChange={(value) => { setCountry(value); setPage(1); }} />
            </div>
            <div className="grid gap-1 text-sm">
              <span className="font-medium text-zinc-300">Month</span>
              <SmoothSelect ariaLabel="Month" value={month} options={filters.data?.months ?? []} placeholder="All primary-scope months" onChange={(value) => { setMonth(value); setPage(1); }} />
            </div>
            <button className="soft-button w-full self-end rounded-md px-4 py-2 text-sm md:w-auto" onClick={() => { setCountry(""); setMonth(""); setPage(1); }}>Clear</button>
          </div>
        </section>
        <FxWarning data={budget.data} />
        <BudgetCards data={budget.data} />
        <LocalCurrencyBreakdown data={budget.data} />
        {budget.data.rows.length ? (
          <div className="grid min-w-0 grid-cols-1 items-start gap-5">
            <BudgetSpendChart data={budget.data} />
            <BudgetGapTable
              data={budget.data}
              page={page}
              sort={sort}
              onPageChange={setPage}
              onSort={(column) => { setSort((current) => nextSort(current, column)); setPage(1); }}
            />
          </div>
        ) : (
          <EmptyState title="No budget rows" detail="No budget data matches the current analytical scope." />
        )}
      </div>
    </main>
  );
}
