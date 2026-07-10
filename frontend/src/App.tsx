import { lazy, Suspense, useState, type ReactNode } from "react";
import { Activity, ArrowRight, DatabaseZap, LogOut, Sparkles, Stethoscope, UploadCloud, WalletCards, type LucideIcon } from "lucide-react";

import { AiAssistantPanel } from "./components/ai/AiAssistantPanel";
import { DataFreshnessBanner, LoadingState } from "./components/common/DataStateComponents";
import { SidePanel } from "./components/common/SidePanel";
import { WarningCenterDock, WarningCenterProvider } from "./components/common/WarningCenter";
import { DataUploadPanel } from "./components/ingestion/DataUploadPanel";
import { useDashboardMeta } from "./hooks/useDashboardMeta";
const BudgetUtilization = lazy(() => import("./pages/BudgetUtilization").then((module) => ({ default: module.BudgetUtilization })));
const DataQuality = lazy(() => import("./pages/DataQuality").then((module) => ({ default: module.DataQuality })));
const DoctorRoi = lazy(() => import("./pages/DoctorRoi").then((module) => ({ default: module.DoctorRoi })));
const ExecutionMatrix = lazy(() => import("./pages/ExecutionMatrix").then((module) => ({ default: module.ExecutionMatrix })));

type PageKey = "execution" | "budget" | "doctors" | "quality";
type AiContext = { pageContext: string; filters: Record<string, unknown> };

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
  const [uploadOpen, setUploadOpen] = useState(false);
  const [aiContext, setAiContext] = useState<AiContext>({ pageContext: "execution", filters: {} });
  const meta = useDashboardMeta();

  function enterApp() {
    if (entryExiting) return;
    setEntryExiting(true);
    window.setTimeout(() => setEntered(true), 560);
  }

  function returnToEntry() {
    setPage("execution");
    setEntryExiting(false);
    setEntered(false);
  }

  if (!entered) {
    return <EntryScreen exiting={entryExiting} onEnter={enterApp} />;
  }

  return (
    <WarningCenterProvider>
      <div className="min-h-screen animate-page-enter bg-surface text-ink">
        <nav className="sticky top-0 z-40 border-b border-white/[0.08] bg-[#07090a]/88 px-4 py-3 shadow-[0_18px_50px_rgba(0,0,0,0.24)] backdrop-blur-2xl">
          <div className="mx-auto flex max-w-7xl min-w-0 flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <button
              onClick={returnToEntry}
              className="group -ml-2 flex min-w-0 items-center gap-3 rounded-lg px-2 py-1.5 text-left transition-all duration-500 ease-out"
              aria-label="Return to loading screen"
              title="Return to loading screen"
            >
              <CiplaLogoPlaceholder size="sm" />
              <div className="min-w-0 ml-5">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="truncate text-lg font-semibold tracking-tight bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent transition-all duration-500 ">Cipla Execution Intelligence</p>
                </div>
                <p className="text-xs bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Planner, consolidation, RCPA, workflow, budget, ROI, and data-quality governance</p>
                <p className="mt-1 text-[0.68rem] font-medium uppercase tracking-[0.22em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Engineered by Aditya Nema</p>
                
              </div>
            </button>
            <div className="-mx-1 flex max-w-full items-center gap-2 overflow-x-auto px-3 p-1 lg:mx-0 lg:shrink-0">
              <div className="flex shrink-0 gap-2">
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
              <div className="h-8 w-px shrink-0 bg-white/[0.08]" aria-hidden="true" />
              <button
                type="button"
                onClick={() => setUploadOpen(true)}
                className="soft-button flex shrink-0 items-center gap-2 rounded-md border-accent/20 bg-accent/[0.07] px-3 py-2 text-sm text-cyan-100 hover:border-accent/40 hover:bg-accent/[0.13]"
                aria-label="Upload new data files"
                title="Upload new data/files"
              >
                <UploadCloud aria-hidden="true" className="h-4 w-4" />
                Upload new data/files
              </button>
              <button
                type="button"
                onClick={returnToEntry}
                className="soft-button flex shrink-0 items-center gap-2 rounded-md border-red-300/10 px-3 py-2 text-sm text-red-300/90 hover:border-red-300/25 hover:bg-red-400/[0.2] hover:text-red-50"
                aria-label="Exit to loading screen"
                title="Exit to loading screen"
              >
                <LogOut aria-hidden="true" className="h-4 w-4" />
                Exit
              </button>
            </div>
          </div>
        </nav>
        {meta.data && page === "execution" ? (
          <div className="mx-auto max-w-7xl px-4 pt-4 sm:px-6">
            <DataFreshnessBanner meta={meta.data.meta} />
          </div>
        ) : null}
        <Suspense fallback={<main><LoadingState label="Loading dashboard" /></main>}>
          {page === "execution" ? <ExecutionMatrix onAiContextChange={setAiContext} /> : null}
          {page === "budget" ? <BudgetUtilization onAiContextChange={setAiContext} /> : null}
          {page === "doctors" ? <DoctorRoi onAiContextChange={setAiContext} /> : null}
          {page === "quality" ? <DataQuality onAiContextChange={setAiContext} /> : null}
        </Suspense>
      </div>
      <WarningCenterDock />
      <AiAssistantPanel context={aiContext} />
      <SidePanel open={uploadOpen} onClose={() => setUploadOpen(false)} widthClass="sm:max-w-2xl">
        <DataUploadPanel onClose={() => setUploadOpen(false)} />
      </SidePanel>
    </WarningCenterProvider>
  );
}

function EntryScreen({ exiting, onEnter }: { exiting: boolean; onEnter: () => void }) {
  return (
    <main className={`relative flex min-h-screen overflow-hidden bg-[#07090a] text-ink transition-all duration-500 ease-out ${exiting ? "scale-[1.01] opacity-0 blur-sm" : "scale-100 opacity-100 blur-0"}`}>
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(135deg,rgba(97,199,187,0.12),transparent_34%),linear-gradient(180deg,rgba(255,255,255,0.045),transparent_48%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-accent/[0.07] to-transparent" />
      <section className="relative mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-10 px-5 py-10 sm:px-8 lg:grid-cols-[minmax(0,0.95fr)_minmax(22rem,0.65fr)]">
        <div className="max-w-4xl animate-page-enter">
          <div className="transition-all duration-700 hover:scale-y-[1.05] hover:opacity-90"><CiplaLogoPlaceholder size="lg"/></div>
          
          <p className="mt-8 text-sm font-semibold uppercase tracking-[0.24em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">Cipla EMEU/PBP analytics</p>
          <h1 className="mt-4 pb-[6px] max-w-4xl text-4xl font-semibold bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent ">
            Doctor ROI and Execution Intelligence for regional investment decisions.
          </h1>
          <p className="mt-5 max-w-3xl text-base leading-7 text-zinc-300">
            Built to orchestrate 50+ regional investment decisions per month across 6 countries by converting fragmented planner, execution, consolidation, workflow, budget, and RCPA workbooks into one auditable decision layer.
          </p>
          <div className="mt-7 grid max-w-4xl grid-cols-1 gap-3 sm:grid-cols-2">
            <EntryFeature icon={<Stethoscope className="h-4 w-4" />} title="Doctor ROI" detail="Surfaces ROI quadrants, dark-horse doctors, high-value engaged physicians, and no-RCPA limitations." />
            <EntryFeature icon={<Activity className="h-4 w-4" />} title="Execution governance" detail="Reconciles planned events, execution snapshots, consolidation requests, workflow owners, and intervention mix." />
            <EntryFeature icon={<WalletCards className="h-4 w-4" />} title="Budget control" detail="Separates planned, confirmed, BTU, BTC, actual spend, unspent gaps, overruns, and FX quality." />
            <EntryFeature icon={<Sparkles className="h-4 w-4" />} title="ExecAI" detail="Embedded structured RAG assistant with query planning, evidence validation, redaction, and deterministic fallback." />
          </div>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={onEnter}
              disabled={exiting}
              className="animate-pulse group inline-flex items-center gap-3 rounded-lg border border-accent/30 bg-accent/[0.13] px-5 py-3 text-sm font-semibold text-zinc-50 shadow-[0_18px_46px_rgba(97,199,187,0.12)] transition-all duration-500 ease-out hover:-translate-y-0.5 hover:border-accent/55 hover:bg-accent/[0.18] hover:shadow-[0_24px_56px_rgba(97,199,187,0.18)] focus:outline-none focus:ring-2 focus:ring-accent/30 active:translate-y-0"
            >
              Click to continue
              <ArrowRight className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1" />
            </button>
            <p className="text-xs font-medium uppercase tracking-[0.22em] text-cyan-200/80">Engineered by Aditya Nema</p>
          </div>
        </div>

        <aside className="dashboard-card relative overflow-hidden p-5">
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.055] to-transparent" />
          <div className="relative">
            <div className="flex items-center gap-2 text-accent">
              <Sparkles className="h-4 w-4" />
              <p className="text-xs font-semibold uppercase tracking-[0.24em]">Platform evidence</p>
            </div>
            <div className="mt-5 grid gap-3 text-sm text-zinc-300">
              <MetricLine label="Rows normalized" value="1M+" detail="Raw Excel/XLSB rows into auditable PostgreSQL KPI views." />
              <MetricLine label="Architecture" value="FastAPI + Supabase + React" detail="Automated Python ETL with typed APIs and a reusable dashboard." />
              <MetricLine label="Decision views" value="ROI, budget, workflow" detail="Dynamic visualizations for quadrants, tables, utilization, and bottlenecks." />
              <MetricLine label="Reliability" value="100+ test definitions" detail="Covers ETL edge cases, financial mappings, frontend states, and AI grounding." />
            </div>
            <div className="mt-6 rounded-lg border border-white/[0.08] bg-black/20 p-4">
              <p className="text-xs uppercase tracking-wide text-zinc-500">Built for</p>
              <p className="mt-2 text-lg font-semibold text-zinc-50">Cipla EMEU doctor investment governance</p>
              <p className="mt-1 text-sm text-zinc-400">Fast reviews, clean audit trail, and practical doctor ROI decisions from raw field data.</p>
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

function MetricLine({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-lg border border-white/[0.08] bg-black/20 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-zinc-50">{value}</p>
      <p className="mt-1 text-xs leading-5 text-zinc-500">{detail}</p>
    </div>
  );
}
