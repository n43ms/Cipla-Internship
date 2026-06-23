import { lazy, Suspense, useState, type ReactNode } from "react";
import { Activity, ArrowRight, DatabaseZap, ShieldCheck, Sparkles, Stethoscope, WalletCards, type LucideIcon } from "lucide-react";

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
  const [entered, setEntered] = useState(false);
  const [entryExiting, setEntryExiting] = useState(false);
  const meta = useDashboardMeta();

  function enterApp() {
    if (entryExiting) return;
    setEntryExiting(true);
    window.setTimeout(() => setEntered(true), 560);
  }

  if (!entered) {
    return <EntryScreen exiting={entryExiting} onEnter={enterApp} />;
  }

  return (
    <div className="min-h-screen animate-page-enter bg-surface text-ink">
      <nav className="sticky top-0 z-40 border-b border-white/[0.08] bg-[#07090a]/88 px-4 py-3 shadow-[0_18px_50px_rgba(0,0,0,0.24)] backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl min-w-0 flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex min-w-0 items-center gap-3">
            <CiplaLogoPlaceholder size="sm" />
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <p className="truncate text-lg font-semibold tracking-tight bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Cipla Execution Intelligence</p>
                <span className="rounded-full border border-accent/20 bg-accent/[0.07] px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide text-accent">
                  Governance cockpit
                </span>
              </div>
              <p className="text-xs bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Planner, consolidation, RCPA, workflow, budget, ROI, and data-quality governance</p>
              <p className="mt-1 text-[0.68rem] font-medium uppercase tracking-[0.22em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Engineered by Aditya Nema</p>
            </div>
          </div>
          <div className="-mx-1 flex max-w-full gap-2 overflow-x-auto px-3 p-1 lg:mx-0 lg:shrink-0">
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

function EntryScreen({ exiting, onEnter }: { exiting: boolean; onEnter: () => void }) {
  return (
    <main className={`relative flex min-h-screen overflow-hidden bg-[#07090a] text-ink transition-all duration-500 ease-out ${exiting ? "scale-[1.01] opacity-0 blur-sm" : "scale-100 opacity-100 blur-0"}`}>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(97,199,187,0.18),transparent_32%),radial-gradient(circle_at_78%_24%,rgba(126,144,255,0.12),transparent_30%),linear-gradient(135deg,rgba(255,255,255,0.04),transparent_42%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-56 bg-gradient-to-t from-accent/[0.08] to-transparent" />
      <section className="relative mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[minmax(0,0.95fr)_minmax(22rem,0.65fr)]">
        <div className="max-w-4xl animate-page-enter">
          <CiplaLogoPlaceholder size="lg" />
          <p className="mt-8 text-lg font-semibold uppercase tracking-[0.32em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Execution intelligence platform</p>
          <h1 className="mt-4 max-w-4xl text-4xl font-semibold tracking-tight bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent  sm:text-2xl lg:text-4xl">
            One command center for planning, execution, budget control, workflow proof, and doctor ROI.
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">
            This software turns messy planner, consolidation, RCPA, execution, and workflow Excel data into a governed dashboard with auditable matching, budget utilization, intervention mix, doctor opportunity scoring, and data-quality checks.
          </p>
          <div className="mt-7 grid max-w-3xl grid-cols-1 gap-3 sm:grid-cols-3">
            <EntryFeature icon={<ShieldCheck className="h-4 w-4" />} title="Auditable data" detail="Tracks source files, validation warnings, scope rules, and match coverage." />
            <EntryFeature icon={<Activity className="h-4 w-4" />} title="Execution cockpit" detail="Compares planned events against snapshots and consolidation evidence." />
            <EntryFeature icon={<Stethoscope className="h-4 w-4" />} title="Doctor ROI" detail="Connects attended doctors, spend allocation, and historical RCPA baselines." />
          </div>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={onEnter}
              disabled={exiting}
              className="group inline-flex items-center gap-3 rounded-lg border border-accent/30 bg-accent/[0.13] px-5 py-3 text-sm font-semibold text-zinc-50 shadow-[0_18px_46px_rgba(97,199,187,0.12)] transition-all duration-500 ease-out hover:-translate-y-0.5 hover:border-accent/55 hover:bg-accent/[0.18] hover:shadow-[0_24px_56px_rgba(97,199,187,0.18)] focus:outline-none focus:ring-2 focus:ring-accent/30 active:translate-y-0"
            >
              Click to continue
              <ArrowRight className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1" />
            </button>
            <p className="text-xs font-medium uppercase tracking-[0.22em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Engineered by Aditya Nema</p>
          </div>
        </div>

        <aside className="dashboard-card relative overflow-hidden p-5">
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.06] to-transparent" />
          <div className="relative">
            <div className="flex items-center gap-2 text-accent">
              <Sparkles className="h-4 w-4" />
              <p className="text-xs font-semibold uppercase tracking-[0.24em]">What it does</p>
            </div>
            <div className="mt-5 space-y-4 text-sm text-zinc-300">
              <p>Normalizes XLSX/XLSB source files into production-grade Supabase tables.</p>
              <p>Reconciles planner rows, monthly execution snapshots, consolidation requests, and report workflow status.</p>
              <p>Separates matched evidence from actual execution so leadership views stay honest.</p>
              <p>Highlights budget gaps, FX quality, pending reports, unmatched records, and doctor-level opportunities.</p>
            </div>
            <div className="mt-6 rounded-lg border border-white/[0.08] bg-black/20 p-4">
              <p className="text-xs uppercase tracking-wide text-zinc-500">Built for</p>
              <p className="mt-2 text-lg font-semibold text-zinc-50">Cipla EMEU execution governance</p>
              <p className="mt-1 text-sm text-zinc-500">Fast reviews. Clean audit trail. Practical decisions from messy field data.</p>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function CiplaLogoPlaceholder({ size }: { size: "sm" | "lg" }) {
  const large = size === "lg";
  return (
    <div className={`relative ml-7 grid shrink-0 place-items-center ${large ? "h-32 w-48" : "h-16 w-24"}`} aria-label="Cipla logo">
      <div className="absolute inset-[-18%] rounded-[2rem] bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,1)_0%,rgba(255,255,255,1)_37%,rgba(255,255,255,0)_65%)]" />
      <div className="absolute inset-[-4%] rounded-[1.5rem] bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,1)_0%,rgba(255,255,255,1)_37%,rgba(255,255,255,0)_65%)]" />
      <div className={`relative grid place-items-center ${large ? "h-24 w-36" : "h-11 w-16"}`}>
        <img
          src="/cipla-logo.png"
          alt="Cipla logo"
          className={`${large ? "max-h-[4.75rem] max-w-[7.75rem]" : "max-h-8 max-w-12"} object-contain`}
        />
      </div>
    </div>
  );
}

function EntryFeature({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-white/[0.035] p-4 transition-all duration-500 ease-out hover:-translate-y-0.5 hover:border-accent/20 hover:bg-white/[0.055]">
      <div className="flex items-center gap-2 text-accent">
        {icon}
        <p className="text-sm font-semibold text-zinc-100">{title}</p>
      </div>
      <p className="mt-2 text-xs leading-5 text-zinc-500">{detail}</p>
    </div>
  );
}
