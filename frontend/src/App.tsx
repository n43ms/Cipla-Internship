import { lazy, Suspense, useState } from "react";

import { DataFreshnessBanner } from "./components/common/DataStateComponents";
import { useDashboardMeta } from "./hooks/useDashboardMeta";
const BudgetUtilization = lazy(() => import("./pages/BudgetUtilization").then((module) => ({ default: module.BudgetUtilization })));
const DataQuality = lazy(() => import("./pages/DataQuality").then((module) => ({ default: module.DataQuality })));
const DoctorRoi = lazy(() => import("./pages/DoctorRoi").then((module) => ({ default: module.DoctorRoi })));
const ExecutionMatrix = lazy(() => import("./pages/ExecutionMatrix").then((module) => ({ default: module.ExecutionMatrix })));

type PageKey = "execution" | "budget" | "doctors" | "quality";

const PAGES: Array<{ key: PageKey; label: string }> = [
  { key: "execution", label: "Execution" },
  { key: "budget", label: "Budget" },
  { key: "doctors", label: "Doctor ROI" },
  { key: "quality", label: "Data Quality" },
];

export default function App() {
  const [page, setPage] = useState<PageKey>("execution");
  const meta = useDashboardMeta();
  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-slate-950">Cipla Execution Intelligence</p>
            <p className="text-xs text-slate-500">Planner, consolidation, RCPA, workflow, budget, ROI, and data-quality governance</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {PAGES.map((item) => (
              <button
                key={item.key}
                className={`soft-button rounded-md px-3 py-2 text-sm ${
                  page === item.key ? "bg-slate-950 text-white" : "border border-slate-200 bg-white text-slate-700"
                }`}
                onClick={() => setPage(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </nav>
      {meta.data && page !== "quality" ? (
        <div className="mx-auto max-w-7xl px-4 pt-4 sm:px-6">
          <DataFreshnessBanner meta={meta.data.meta} />
        </div>
      ) : null}
      <Suspense fallback={<main className="p-6 text-sm text-slate-500">Loading dashboard page</main>}>
        {page === "execution" ? <ExecutionMatrix /> : null}
        {page === "budget" ? <BudgetUtilization /> : null}
        {page === "doctors" ? <DoctorRoi /> : null}
        {page === "quality" ? <DataQuality /> : null}
      </Suspense>
    </div>
  );
}
