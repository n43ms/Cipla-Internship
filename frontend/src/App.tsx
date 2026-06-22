import { lazy, Suspense, useState } from "react";
import { Activity, DatabaseZap, Stethoscope, WalletCards, type LucideIcon } from "lucide-react";

import { DataFreshnessBanner, LoadingState } from "./components/common/DataStateComponents";
import { useDashboardMeta } from "./hooks/useDashboardMeta";
const BudgetUtilization = lazy(() => import("./pages/BudgetUtilization").then((module) => ({ default: module.BudgetUtilization })));
const DataQuality = lazy(() => import("./pages/DataQuality").then((module) => ({ default: module.DataQuality })));
const DoctorRoi = lazy(() => import("./pages/DoctorRoi").then((module) => ({ default: module.DoctorRoi })));
const ExecutionMatrix = lazy(() => import("./pages/ExecutionMatrix").then((module) => ({ default: module.ExecutionMatrix })));

type PageKey = "execution" | "budget" | "doctors" | "quality";

const PAGES: Array<{ key: PageKey; label: string; icon: LucideIcon }> = [
  { key: "execution", label: "Execution", icon: Activity },
  { key: "budget", label: "Budget", icon: WalletCards },
  { key: "doctors", label: "Doctor ROI", icon: Stethoscope },
  { key: "quality", label: "Data Quality", icon: DatabaseZap },
];

export default function App() {
  const [page, setPage] = useState<PageKey>("execution");
  const meta = useDashboardMeta();
  return (
    <div className="min-h-screen bg-surface text-ink">
      <nav className="sticky top-0 z-40 border-b border-zinc-800 bg-zinc-950/90 px-4 py-3 shadow-lg shadow-black/10 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl min-w-0 flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-zinc-50">Cipla Execution Intelligence</p>
            <p className="text-xs text-zinc-500">Planner, consolidation, RCPA, workflow, budget, ROI, and data-quality governance</p>
          </div>
          <div className="-mx-1 flex max-w-full gap-2 overflow-x-auto px-1 pb-1 lg:mx-0 lg:shrink-0 lg:px-0">
            {PAGES.map((item) => {
              const Icon = item.icon;
              return (
              <button
                key={item.key}
                className={`soft-button flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm ${
                  page === item.key ? "border-accent/25 bg-accent/[0.07] text-[#abc8c3] shadow-[inset_0_-1px_0_rgba(106,174,165,0.35)]" : ""
                }`}
                onClick={() => setPage(item.key)}
                aria-current={page === item.key ? "page" : undefined}
              >
                <Icon aria-hidden="true" className="h-4 w-4" />
                {item.label}
              </button>
              );
            })}
          </div>
        </div>
      </nav>
      {meta.data && page !== "quality" ? (
        <div className="mx-auto max-w-7xl px-4 pt-4 sm:px-6">
          <DataFreshnessBanner meta={meta.data.meta} />
        </div>
      ) : null}
      <Suspense fallback={<main><LoadingState label="Loading dashboard" /></main>}>
        {page === "execution" ? <ExecutionMatrix /> : null}
        {page === "budget" ? <BudgetUtilization /> : null}
        {page === "doctors" ? <DoctorRoi /> : null}
        {page === "quality" ? <DataQuality /> : null}
      </Suspense>
    </div>
  );
}
