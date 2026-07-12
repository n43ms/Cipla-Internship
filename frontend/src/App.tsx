import { lazy, Suspense, useEffect, useState, type ReactNode } from "react";
import { Activity, ArrowRight, ChevronDown, Code2, DatabaseZap, Info, LogOut, MapPinned, Sparkles, Stethoscope, UploadCloud, WalletCards, X, type LucideIcon } from "lucide-react";

import { AiAssistantPanel } from "./components/ai/AiAssistantPanel";
import { DataFreshnessBanner, KpiCard, LoadingState } from "./components/common/DataStateComponents";
import { SidePanel } from "./components/common/SidePanel";
import { WarningCenterDock, WarningCenterProvider } from "./components/common/WarningCenter";
import { DataUploadPanel } from "./components/ingestion/DataUploadPanel";
import { useDashboardMeta } from "./hooks/useDashboardMeta";
const BudgetUtilization = lazy(() => import("./pages/BudgetUtilization").then((module) => ({ default: module.BudgetUtilization })));
const DataQuality = lazy(() => import("./pages/DataQuality").then((module) => ({ default: module.DataQuality })));
const DoctorRoi = lazy(() => import("./pages/DoctorRoi").then((module) => ({ default: module.DoctorRoi })));
const ExecutionMatrix = lazy(() => import("./pages/ExecutionMatrix").then((module) => ({ default: module.ExecutionMatrix })));
const TerritoryIntelligence = lazy(() => import("./pages/TerritoryIntelligence").then((module) => ({ default: module.TerritoryIntelligence })));

type PageKey = "execution" | "budget" | "doctors" | "territory" | "quality" | "about";
type AiContext = { pageContext: string; filters: Record<string, unknown> };

type NavPage = { key: PageKey; label: string; icon: LucideIcon; iconClass: string; activeClass: string };

const PRIMARY_PAGES: NavPage[] = [
  { key: "doctors", label: "Doctor ROI", icon: Stethoscope, iconClass: "text-sky-300", activeClass: "border-sky-300/25 bg-sky-300/[0.08] text-sky-50 shadow-[inset_3px_0_0_rgba(125,211,252,0.58)]" },
  { key: "execution", label: "Execution", icon: Activity, iconClass: "text-emerald-300", activeClass: "border-emerald-300/25 bg-emerald-300/[0.08] text-emerald-50 shadow-[inset_3px_0_0_rgba(110,231,183,0.55)]" },
  { key: "territory", label: "Territory", icon: MapPinned, iconClass: "text-violet-300", activeClass: "border-violet-300/25 bg-violet-300/[0.08] text-violet-50 shadow-[inset_3px_0_0_rgba(196,181,253,0.52)]" },
];

const OPERATIONS_PAGES: NavPage[] = [
  { key: "budget", label: "Budget", icon: WalletCards, iconClass: "text-amber-200", activeClass: "border-amber-200/25 bg-amber-200/[0.08] text-amber-50 shadow-[inset_3px_0_0_rgba(253,230,138,0.5)]" },
  { key: "quality", label: "Data Quality", icon: DatabaseZap, iconClass: "text-cyan-300", activeClass: "border-cyan-300/25 bg-cyan-300/[0.08] text-cyan-50 shadow-[inset_3px_0_0_rgba(103,232,249,0.52)]" },
];

const HEADER_SUBTITLE = "Doctor ROI, execution follow-up, budget governance, territory coverage, and your personal Decision Intelligence Copilot - ExecAI";

export default function App() {
  const [page, setPage] = useState<PageKey>("doctors");
  const [entered, setEntered] = useState(false);
  const [entryExiting, setEntryExiting] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [showAiNotice, setShowAiNotice] = useState(true);
  const [aiOpenSignal, setAiOpenSignal] = useState(0);
  const [aiContext, setAiContext] = useState<AiContext>({ pageContext: "doctor_roi", filters: {} });
  const [headerCompact, setHeaderCompact] = useState(false);
  const meta = useDashboardMeta();

  useEffect(() => {
    if (!entered) {
      setHeaderCompact(false);
      return undefined;
    }

    function updateHeaderState() {
      setHeaderCompact(window.scrollY > 6);
    }

    updateHeaderState();
    window.addEventListener("scroll", updateHeaderState, { passive: true });
    return () => window.removeEventListener("scroll", updateHeaderState);
  }, [entered]);

  function enterApp() {
    if (entryExiting) return;
    setEntryExiting(true);
    window.setTimeout(() => setEntered(true), 560);
  }

  function returnToEntry() {
    setPage("doctors");
    setEntryExiting(false);
    setEntered(false);
    setShowAiNotice(true);
  }

  function openExecAiFromNotice() {
    setShowAiNotice(false);
    setAiOpenSignal((value) => value + 1);
  }

  if (!entered) {
    return <EntryScreen exiting={entryExiting} onEnter={enterApp} />;
  }

  return (
    <WarningCenterProvider>
      <div className="min-h-screen animate-page-enter bg-surface text-ink">
        <nav className={`sticky top-0 z-40 border-b border-white/[0.08] bg-[#07090a]/88 px-4 shadow-[0_18px_50px_rgba(0,0,0,0.24)] backdrop-blur-2xl transition-all duration-300 ease-out ${headerCompact ? "py-2" : "py-3"}`}>
          <div className={`mx-auto flex max-w-7xl min-w-0 flex-col gap-3 transition-all duration-300 ease-out lg:flex-row lg:items-stretch lg:justify-between ${headerCompact ? "lg:items-center" : ""}`}>
            <button
              onClick={returnToEntry}
              className={`group -ml-2 flex min-w-0 items-center gap-3 rounded-lg px-2 text-left transition-all duration-300 ease-out ${headerCompact ? "py-1 lg:min-h-[4.4rem]" : "py-2 lg:min-h-[10.2rem] lg:self-stretch"}`}
              aria-label="Return to loading screen"
              title="Return to loading screen"
            >
              <CiplaLogoPlaceholder size="sm" />
              <div className={`ml-6 flex min-w-0 flex-1 flex-col justify-center transition-all duration-300 ease-out lg:max-w-[32rem] ${headerCompact ? "gap-0 lg:py-0" : "gap-2 lg:py-2"}`}>
                <div className="min-w-0">
                  <p className={`font-semibold leading-tight tracking-tight bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent transition-all duration-300 ${headerCompact ? "text-xl" : "text-2xl"}`}>Cipla Execution Intelligence</p>
                </div>
                <p className={`max-w-lg text-sm leading-6 bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent transition-all duration-300 ${headerCompact ? "pointer-events-none max-h-0 opacity-0" : "max-h-24 opacity-100"}`}>{HEADER_SUBTITLE}</p>
                <p className={`text-xs font-medium uppercase tracking-[0.22em] bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-200 bg-clip-text text-transparent transition-all duration-300 ${headerCompact ? "pointer-events-none max-h-0 opacity-0" : "max-h-6 opacity-100"}`}>Engineered by Aditya Nema</p>
              </div>
            </button>
            <div className={`-mx-1 flex max-w-full items-stretch gap-3 overflow-visible px-3 p-1 transition-all duration-300 ease-out lg:mx-0 lg:shrink-0 ${headerCompact ? "lg:items-center" : ""}`}>
              <div className={`flex max-w-full shrink min-w-0 gap-3 overflow-visible pr-1 transition-all duration-300 ease-out ${headerCompact ? "items-center" : "items-stretch overflow-x-auto"}`}>
                {headerCompact ? (
                  <>
                    <CompactNavDropdown title="Decision Intelligence" pages={PRIMARY_PAGES} current={page} onSelect={setPage} />
                    <CompactNavDropdown title="Governance" pages={OPERATIONS_PAGES} current={page} onSelect={setPage} />
                  </>
                ) : (
                  <>
                    <NavGroup title="Decision Intelligence" pages={PRIMARY_PAGES} current={page} onSelect={setPage} />
                    <NavGroup title="Governance" pages={OPERATIONS_PAGES} current={page} onSelect={setPage} centered />
                  </>
                )}
              </div>
              <div className="w-px shrink-0 bg-white/[0.08]" aria-hidden="true" />
              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  onClick={() => setUploadOpen(true)}
                  className="soft-button flex shrink-0 items-center gap-2 rounded-lg border-accent/20 bg-accent/[0.07] px-4 py-3 text-sm font-semibold text-cyan-100 hover:border-accent/40 hover:bg-accent/[0.13]"
                  aria-label="Upload new data files"
                  title="Upload new data/files"
                >
                  <UploadCloud aria-hidden="true" className="h-4 w-4 text-cyan-300" />
                  Upload new data/files
                </button>
                <UtilityMenu onAbout={() => setPage("about")} onExit={returnToEntry} />
              </div>
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
          {page === "territory" ? <TerritoryIntelligence onAiContextChange={setAiContext} /> : null}
          {page === "quality" ? <DataQuality onAiContextChange={setAiContext} /> : null}
          {page === "about" ? <AboutSoftware /> : null}
        </Suspense>
      </div>
      <WarningCenterDock />
      {showAiNotice ? <ExecAiEntryNotice onClose={() => setShowAiNotice(false)} onTry={openExecAiFromNotice} /> : null}
      <AiAssistantPanel context={aiContext} openSignal={aiOpenSignal} compactHeader={headerCompact} />
      <SidePanel open={uploadOpen} onClose={() => setUploadOpen(false)} widthClass="sm:max-w-2xl">
        <DataUploadPanel onClose={() => setUploadOpen(false)} />
      </SidePanel>
    </WarningCenterProvider>
  );
}

function ExecAiEntryNotice({ onClose, onTry }: { onClose: () => void; onTry: () => void }) {
  return (
    <aside className="execai-entry-notice" role="status" aria-live="polite">
      <div className="flex min-w-0 items-start gap-3">
        <div className="execai-notice-icon" aria-hidden="true">
          <Sparkles className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-cyan-50">ExecAI is available</p>
          <p className="mt-1 text-xs leading-5 text-zinc-300">
            Ask grounded questions about Doctor ROI, execution risk, budgets, territories, and data quality.
          </p>
          <button type="button" className="mt-3 text-xs font-semibold text-cyan-200 transition hover:text-cyan-50" onClick={onTry}>
            Try ExecAI
          </button>
        </div>
      </div>
      <button type="button" className="execai-notice-close" onClick={onClose} aria-label="Dismiss ExecAI notice">
        <X className="h-4 w-4" />
      </button>
    </aside>
  );
}

function EntryScreen({ exiting, onEnter }: { exiting: boolean; onEnter: () => void }) {
  return (
    <main className={`relative flex min-h-screen overflow-x-hidden bg-[#07090a] text-ink transition-all duration-500 ease-out ${exiting ? "scale-[1.01] opacity-0 blur-sm" : "scale-100 opacity-100 blur-0"}`}>
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(135deg,rgba(97,199,187,0.12),transparent_34%),linear-gradient(180deg,rgba(255,255,255,0.045),transparent_48%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-accent/[0.07] to-transparent" />
      <section className="relative mx-auto grid w-full max-w-7xl grid-cols-1 items-center gap-7 px-5 py-5 sm:px-8 sm:py-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(22rem,0.65fr)]">
        <div className="max-w-4xl animate-page-enter">
          <div className="transition-all duration-700 hover:scale-y-[1.05] hover:opacity-90"><CiplaLogoPlaceholder size="lg"/></div>
          
          <p className="mt-7 text-sm font-semibold uppercase tracking-[0.24em] text-cyan-200/85">Emerging Markets and Europe Patient Benefits Program</p>
          <h1 className="landing-intelligence-text mt-4 pb-[6px] max-w-4xl text-4xl font-semibold">
            Doctor ROI & Execution Intelligence
          </h1>
          <p className="landing-intelligence-copy mt-4 max-w-3xl text-base leading-7">
            A decision dashboard for doctor investment, execution follow-up, budget control, territory coverage, data confidence, and ExecAI-powered business questions.
          </p>
          <div className="mt-5 grid max-w-4xl grid-cols-1 gap-3 sm:grid-cols-2">
            <EntryFeature
              icon={<Stethoscope className="h-4 w-4" />}
              title="Doctor ROI"
              detail="Combines sponsorship history, RCPA signals, prescriptions, no-fee activity, and contract value to guide doctor investment decisions."
            />
            <EntryFeature
              icon={<Activity className="h-4 w-4" />}
              title="Execution follow-up"
              detail="Tracks planned events against approvals, reports, owners, workflow status, and evidence gaps."
            />
            <EntryFeature
              icon={<WalletCards className="h-4 w-4" />}
              title="Budget control"
              detail="Shows planned budget, actual spend, overruns, unspent gaps, and source-backed expense warnings."
            />
            <EntryFeature
              icon={<MapPinned className="h-4 w-4" />}
              title="Territory coverage"
              detail="Flags underserved, overserved, and balanced territories using location, patch, doctor, prescription, and investment data."
            />
            <EntryFeature
              icon={<DatabaseZap className="h-4 w-4" />}
              title="Data confidence"
              detail="Surfaces freshness, loaded files, validation issues, match quality, skipped rows, and coverage gaps."
            />
            <EntryFeature
              icon={<Sparkles className="h-4 w-4" />}
              title="ExecAI"
              detail="Answers business questions about ROI, execution risk, budgets, territories, and data quality using grounded dashboard context."
            />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-4">
            <button
              type="button"
              onClick={onEnter}
              disabled={exiting}
              className="group inline-flex items-center gap-3 rounded-lg border border-accent/30 bg-accent/[0.13] px-5 py-3 text-sm font-semibold text-zinc-50 shadow-[0_18px_46px_rgba(97,199,187,0.12)] transition-all duration-500 ease-out hover:-translate-y-0.5 hover:border-accent/55 hover:bg-accent/[0.18] hover:shadow-[0_24px_56px_rgba(97,199,187,0.18)] focus:outline-none focus:ring-2 focus:ring-accent/30 active:translate-y-0"
            >
              Click to continue
              <ArrowRight className="h-4 w-4 transition-transform duration-500 group-hover:translate-x-1" />
            </button>
            <p className="text-xs font-medium uppercase tracking-[0.22em] text-cyan-200/80">Engineered by Aditya Nema</p>
          </div>
        </div>

        <aside className="dashboard-card relative overflow-hidden p-4">
          <div className="absolute inset-0 bg-gradient-to-br from-white/[0.055] to-transparent" />
          <div className="relative">
            <div className="flex items-center gap-2 text-accent">
              <Sparkles className="h-4 w-4" />
              <p className="text-xs font-semibold uppercase tracking-[0.24em]">Decision scope</p>
            </div>
            <div className="mt-4 grid gap-2.5 text-sm text-zinc-300">
              <MetricLine tone="sky" label="Investment governance" value="Regional cadence" detail="Supports recurring sponsorship and engagement decisions." />
              <MetricLine tone="cyan" label="Doctor ROI" value="Patient benefit lens" detail="Connects doctor spend with prescription and engagement signals." />
              <MetricLine tone="emerald" label="Execution control" value="Plan to proof" detail="Highlights pending reports, blocked owners, and delayed activities." />
              <MetricLine tone="amber" label="Data confidence" value="Audit first" detail="Makes source limits visible before teams act on KPIs." />
            </div>
            <div className="mt-4 rounded-lg border border-white/[0.08] bg-black/20 p-4">
              <p className="text-xs uppercase tracking-wide text-zinc-500">Built for</p>
              <p className="mt-2 text-lg font-semibold text-zinc-50">Cipla Emerging Markets and Europe Patient Benefits Program (EMEU/PBP)</p>
              <p className="mt-1 text-sm text-zinc-400">One decision surface for ROI, execution, budget, territory, and data quality governance.</p>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function NavGroup({
  title,
  pages,
  current,
  centered = false,
  onSelect,
}: {
  title: string;
  pages: NavPage[];
  current: PageKey;
  centered?: boolean;
  onSelect: (page: PageKey) => void;
}) {
  return (
    <div className="grid min-w-[10.25rem] shrink-0 content-start gap-2 rounded-xl border border-white/[0.07] bg-black/20 p-2.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.035)]">
      <p className="px-1 text-[0.66rem] font-semibold uppercase tracking-[0.18em] text-cyan-100">{title}</p>
      <NavColumn pages={pages} current={current} centered={centered} onSelect={onSelect} />
    </div>
  );
}

function NavColumn({ pages, current, centered, onSelect }: { pages: NavPage[]; current: PageKey; centered?: boolean; onSelect: (page: PageKey) => void }) {
  return (
    <div className={`grid min-h-[8rem] gap-2 ${centered ? "content-center" : "content-start"}`}>
      {pages.map((item) => {
        const Icon = item.icon;
        const isActive = current === item.key;
        return (
          <button
            key={item.key}
            className={`soft-button flex min-h-10 w-full shrink-0 items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-semibold ${
              isActive ? item.activeClass : "text-zinc-300"
            }`}
            onClick={() => onSelect(item.key)}
            aria-current={isActive ? "page" : undefined}
          >
            <Icon aria-hidden="true" className={`h-4 w-4 shrink-0 ${item.iconClass}`} />
            <span className="truncate">{item.label}</span>
          </button>
        );
      })}
    </div>
  );
}

function CompactNavDropdown({ title, pages, current, onSelect }: { title: string; pages: NavPage[]; current: PageKey; onSelect: (page: PageKey) => void }) {
  const activePage = pages.find((item) => item.key === current);
  const ActiveIcon = activePage?.icon ?? pages[0]?.icon;

  return (
    <details className="group relative z-[90] shrink-0">
      <summary className="soft-button flex min-h-11 cursor-pointer list-none items-center gap-2 rounded-lg border-cyan-200/[0.11] bg-[#111719] px-3.5 py-2.5 text-sm font-semibold text-cyan-50 shadow-[0_12px_34px_rgba(0,0,0,0.28)] marker:hidden hover:border-cyan-200/22 hover:bg-[#131d21]">
        {ActiveIcon ? <ActiveIcon className={`h-4 w-4 ${activePage?.iconClass ?? "text-cyan-300"}`} aria-hidden="true" /> : null}
        <span className="hidden max-w-[10rem] truncate xl:inline">{title}</span>
        <span className="max-w-[8rem] truncate xl:hidden">{activePage?.label ?? title}</span>
        <ChevronDown className="h-4 w-4 text-cyan-100/70 transition-transform duration-200 group-open:rotate-180" aria-hidden="true" />
      </summary>
      <div className="absolute left-0 top-[calc(100%+0.55rem)] z-[120] grid min-w-64 gap-1 rounded-xl border border-cyan-200/[0.12] bg-[#111315] p-2 shadow-[0_24px_70px_rgba(0,0,0,0.58),0_0_24px_rgba(103,232,249,0.06)] backdrop-blur-2xl">
        <p className="px-2 pb-1 pt-1 text-[0.65rem] font-semibold uppercase tracking-[0.18em] text-cyan-200/70">{title}</p>
        {pages.map((item) => {
          const Icon = item.icon;
          const isActive = current === item.key;
          return (
            <button
              key={item.key}
              type="button"
              className={`flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-semibold transition-colors duration-200 hover:bg-white/[0.055] ${
                isActive ? item.activeClass : "text-zinc-300"
              }`}
              onClick={(event) => {
                onSelect(item.key);
                event.currentTarget.closest("details")?.removeAttribute("open");
              }}
              aria-current={isActive ? "page" : undefined}
            >
              <Icon className={`h-4 w-4 shrink-0 ${item.iconClass}`} aria-hidden="true" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </details>
  );
}

function UtilityMenu({ onAbout, onExit }: { onAbout: () => void; onExit: () => void }) {
  return (
    <details className="group relative z-[80] shrink-0">
      <summary className="soft-button flex cursor-pointer list-none items-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold text-zinc-200 marker:hidden">
        <span>Menu</span>
        <ChevronDown className="h-4 w-4 text-zinc-400 transition-transform duration-200 group-open:rotate-180" aria-hidden="true" />
      </summary>
      <div className="absolute right-0 top-[calc(100%+0.5rem)] z-[90] grid min-w-52 gap-1 rounded-xl border border-white/[0.09] bg-[#111315] p-2 shadow-2xl shadow-black/40">
        <button
          type="button"
          onClick={onAbout}
          className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-zinc-200 transition-colors duration-200 hover:bg-white/[0.06]"
        >
          <Info className="h-4 w-4 text-cyan-300" aria-hidden="true" />
          About this software
        </button>
        <button
          type="button"
          onClick={onExit}
          className="flex items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-200 transition-colors duration-200 hover:bg-red-400/[0.12]"
        >
          <LogOut className="h-4 w-4 text-red-300" aria-hidden="true" />
          Exit
        </button>
      </div>
    </details>
  );
}

function AboutSoftware() {
  return (
    <main className="px-4 py-4 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-3">
        <header>
          <p className="eyebrow">About</p>
          <h1 className="text-2xl font-semibold mt-1 -ml-[0.5px] tracking-tight text-ink">About this software</h1>
          <p className="mt-2 max-w-5xl text-sm leading-6 text-muted">
            Cipla Execution Intelligence was engineered by Aditya Nema for Cipla's Emerging Markets and Europe Patient Benefits Program, turning fragmented field workbooks into an auditable regional doctor investment governance platform.
          </p>
        </header>
        <section className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 xl:grid-cols-4">
          <AboutMetric label="Business program" value="6 markets" detail="Decision layer for the Emerging Markets and Europe Patient Benefits Program across doctor ROI, execution, territory, budget, and quality review." />
          <AboutMetric label="Decision throughput" value="50+/month" detail="Built to support recurring regional investment decisions across sponsorships, conferences, paid/no-fee engagement, workflow follow-up, and execution evidence." />
          <AboutMetric label="Data foundation" value="1.17M rows seen" detail="Documented real-file dry run profiled 8 workbooks and loaded 423,693 compact online records from raw Excel/XLSB sources." />
          <AboutMetric label="Source coverage" value="7 source families" detail="Planner, execution snapshots, consolidated smart-contract reports, workflow statuses, RCPA prescriptions, MSL doctor master, and sponsorship/doctor engagement files." />
          <AboutMetric label="Decision modules" value="5 views + ExecAI" detail="Doctor ROI, Execution, Territory, Budget, Data Quality, business-user upload, warning center, and embedded natural-language analysis." />
          <AboutMetric label="Architecture" value="React + FastAPI" detail="TypeScript dashboard, Python/FastAPI service layer, Supabase PostgreSQL canonical tables, materialized KPI views, and local ingestion tooling." />
          <AboutMetric label="Data integrity" value="Auditable joins" detail="Country-scoped P-codes, source lineage, duplicate detection, schema profiling, validation issues, match confidence, row counts, and materialized-view refreshes." />
          <AboutMetric label="Reliability" value="100+ tests" detail="Coverage across ingestion edge cases, financial mappings, event reconciliation, doctor ROI, API contracts, frontend states, and AI grounding behavior." />
        </section>
        <section className="grid grid-cols-1 gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(20rem,0.72fr)]">
          <div className="dashboard-card p-4">
            <div className="flex items-center gap-2 text-cyan-200">
              <Code2 className="h-4 w-4" aria-hidden="true" />
              <h2 className="font-semibold text-zinc-50">Engineering overview</h2>
            </div>
            <p className="mt-3 text-sm leading-5 text-zinc-300">
              The software combines a React and TypeScript executive dashboard, Python/FastAPI backend services, Supabase PostgreSQL KPI views, and a reusable Excel ingestion pipeline for messy planner, consolidation, workflow, RCPA, and doctor master workbooks.
            </p>
            <p className="mt-2 text-sm leading-5 text-zinc-400">
              ExecAI adds a structured RAG assistant with query planning, PostgreSQL-grounded context, redaction, evidence validation, and deterministic fallback behavior for decision support without replacing the underlying formulas and views.
            </p>
          </div>
          <div className="execai-built-card dashboard-card border-cyan-200/[0.075] bg-[linear-gradient(145deg,rgba(8,13,18,0.97),rgba(13,22,31,0.97)_48%,rgba(10,24,29,0.97))] p-4 shadow-[0_28px_90px_rgba(0,0,0,0.24),0_0_24px_rgba(103,232,249,0.045)]">
            <div className="flex items-center gap-2 text-cyan-200">
              <Sparkles className="h-4 w-4" aria-hidden="true" />
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200/80">Built by</h2>
            </div>
            <p className="mt-3 text-2xl font-semibold text-cyan-50">Aditya Nema</p>
            <p className="mt-2 text-sm leading-5 text-cyan-100/72">
              Designed and implemented for Cipla EMEU/PBP as a production-grade analytics workflow: typed API contracts, source-backed audit trails, deterministic cleaning, modular frontend components, and validation coverage for data and AI behavior.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}

function AboutMetric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="dashboard-card bg-[linear-gradient(135deg,rgba(103,232,249,0.055),rgba(21,23,25,0.96)_42%)] p-3">
      <p className="text-[0.66rem] uppercase tracking-wide text-cyan-200/75">{label}</p>
      <p className="mt-1 text-lg font-semibold text-cyan-50">{value}</p>
      <p className="mt-1 text-[0.72rem] leading-4 text-zinc-500">{detail}</p>
    </div>
  );
}

function CiplaLogoPlaceholder({ size }: { size: "sm" | "lg" }) {
  const large = size === "lg";
  return (
    <div className={`relative ml-7 grid shrink-0 place-items-center ${large ? "h-32 w-48" : "h-20 w-[7.5rem]"}`} aria-label="Cipla logo">
      <div className="absolute inset-[-18%] rounded-[2rem] bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,1)_0%,rgba(255,255,255,1)_37%,rgba(255,255,255,0)_65%)]" />
      <div className="absolute inset-[-4%] rounded-[1.5rem] bg-[radial-gradient(ellipse_at_center,rgba(255,255,255,1)_0%,rgba(255,255,255,1)_37%,rgba(255,255,255,0)_65%)]" />
      <div className={`relative grid place-items-center ${large ? "h-24 w-36" : "h-14 w-20"}`}>
        <img
          src="/cipla-logo.png"
          alt="Cipla logo"
          className={`${large ? "max-h-[4.75rem] max-w-[7.75rem]" : "max-h-10 max-w-16"} object-contain`}
        />
      </div>
    </div>
  );
}

function EntryFeature({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <div className="landing-intelligence-card rounded-lg border border-cyan-200/[0.075] p-3.5 transition-all duration-500 ease-out hover:-translate-y-0.5">
      <div className="flex items-center gap-2 text-cyan-200">
        {icon}
        <p className="text-sm font-semibold text-cyan-50">{title}</p>
      </div>
      <p className="mt-1.5 text-xs leading-[1.35rem] text-cyan-100/58">{detail}</p>
    </div>
  );
}

type LandingTone = "cyan" | "sky" | "emerald" | "amber";

const LANDING_TONE_CLASSES: Record<LandingTone, { card: string; label: string; value: string }> = {
  cyan: {
    card: "bg-cyan-300/[0.045]",
    label: "text-cyan-200/75",
    value: "text-cyan-50",
  },
  sky: {
    card: "bg-sky-300/[0.045]",
    label: "text-sky-200/75",
    value: "text-sky-50",
  },
  emerald: {
    card: "bg-emerald-300/[0.045]",
    label: "text-emerald-200/75",
    value: "text-emerald-50",
  },
  amber: {
    card: "bg-amber-300/[0.045]",
    label: "text-amber-200/75",
    value: "text-amber-50",
  },
};

function MetricLine({ label, value, detail, tone }: { label: string; value: string; detail: string; tone: LandingTone }) {
  const toneClasses = LANDING_TONE_CLASSES[tone];
  return (
    <div className={`relative rounded-lg border border-white/[0.08] p-3 ${toneClasses.card}`}>
      <p className={`text-xs font-medium uppercase tracking-wide ${toneClasses.label}`}>{label}</p>
      <p className={`mt-1 text-base font-semibold ${toneClasses.value}`}>{value}</p>
      <p className="mt-1 text-xs leading-5 text-zinc-500">{detail}</p>
    </div>
  );
}
