import type { ResponseMeta } from "../../types/api";
import { LoaderCircle } from "lucide-react";
import { WarningRegistration } from "./WarningCenter";

export function DataFreshnessBanner({ meta }: { meta?: ResponseMeta }) {
  if (!meta) return null;
  const hasWarnings = meta.dataQualityFlags.length > 0 || meta.limitations.length > 0;
  return (
    <WarningRegistration
      record={{
        id: "data-freshness",
        title: "Data freshness",
        tone: hasWarnings ? "warning" : "success",
        detail: `Latest ingestion: ${meta.latestIngestionStatus}. Generated ${new Date(meta.generatedAt).toLocaleString()}`,
        items: hasWarnings ? [...meta.dataQualityFlags, ...meta.limitations] : [],
      }}
    />
  );
}

export function LimitationList({ limitations }: { limitations: string[] }) {
  const unique = Array.from(new Set(limitations)).filter(Boolean);
  if (!unique.length) return null;
  return (
    <ul className="mt-3 grid grid-cols-1 gap-1 text-xs text-[#bbaa83] sm:grid-cols-2">
      {unique.map((item) => (
        <li key={item} className="rounded-md border border-[#6d5c32]/35 bg-black/20 px-2 py-1">{humanize(item)}</li>
      ))}
    </ul>
  );
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="dashboard-card p-6 text-center">
      <p className="font-semibold text-zinc-200">{title}</p>
      <p className="mt-1 text-sm text-zinc-500">{detail}</p>
    </div>
  );
}

export function ErrorState({ title = "Dashboard data unavailable" }: { title?: string }) {
  return (
    <div className="dashboard-card border-red-400/30 bg-red-400/[0.07] p-6">
      <p className="font-semibold text-red-200">{title}</p>
      <p className="mt-1 text-sm text-red-300/80">The backend could not return this API. Check the server logs and migration state.</p>
    </div>
  );
}

export function LoadingState({ label = "Loading dashboard data", compact = false }: { label?: string; compact?: boolean }) {
  return (
    <div className={`flex w-full items-center justify-center ${compact ? "min-h-48" : "min-h-[55vh]"}`} role="status" aria-live="polite">
      <div className="flex flex-col items-center gap-3 rounded-lg bg-zinc-950/40 px-6 py-5 shadow-xl shadow-black/15 backdrop-blur-sm">
        <span className="relative flex h-10 w-10 items-center justify-center">
          <span className="absolute inset-0 animate-ping rounded-full bg-accent/10" />
          <LoaderCircle aria-hidden="true" className="relative h-12 w-12 animate-spin text-accent" strokeWidth={1.8} />
        </span>
        <p className="text-lg font-medium text-zinc-400">{label}</p>
      </div>
    </div>
  );
}

type KpiTone = "cyan" | "sky" | "emerald" | "amber" | "red" | "violet";

const KPI_TONE_CLASSES: Record<KpiTone, { card: string; label: string; value: string }> = {
  cyan: {
    card: "bg-[linear-gradient(135deg,rgba(103,232,249,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-cyan-200/75",
    value: "text-cyan-50",
  },
  sky: {
    card: "bg-[linear-gradient(135deg,rgba(125,211,252,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-sky-200/75",
    value: "text-sky-50",
  },
  emerald: {
    card: "bg-[linear-gradient(135deg,rgba(110,231,183,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-emerald-200/75",
    value: "text-emerald-50",
  },
  amber: {
    card: "bg-[linear-gradient(135deg,rgba(251,191,36,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-amber-200/75",
    value: "text-amber-50",
  },
  red: {
    card: "bg-[linear-gradient(135deg,rgba(248,113,113,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-red-200/75",
    value: "text-red-50",
  },
  violet: {
    card: "bg-[linear-gradient(135deg,rgba(196,181,253,0.07),rgba(21,23,25,0.96)_42%)]",
    label: "text-violet-200/75",
    value: "text-violet-50",
  },
};

export function KpiCard({ label, value, detail, tone }: { label: string; value: string | number; detail?: string; tone?: KpiTone }) {
  const toneClasses = KPI_TONE_CLASSES[tone ?? inferKpiTone(label)];
  return (
    <div className={`dashboard-card relative p-4 ${toneClasses.card}`}>
      <p className={`text-xs uppercase tracking-wide ${toneClasses.label}`}>{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${toneClasses.value}`}>{value}</p>
      {detail ? <p className="mt-1 text-xs text-zinc-500">{detail}</p> : null}
    </div>
  );
}

function inferKpiTone(label: string): KpiTone {
  const normalized = label.toLowerCase();
  if (/\b(missing|issue|skipped|unmatched|gap|unspent|no rcpa)\b/.test(normalized)) return "amber";
  if (/\b(error|rejected|failed|leakage|overrun)\b/.test(normalized)) return "red";
  if (/\b(confirmed|approved|executed|loaded|reliability|integrity)\b/.test(normalized)) return "emerald";
  if (/\b(doctor|roi|rcpa|pcode|match|coverage|quality|confidence)\b/.test(normalized)) return "cyan";
  if (/\b(budget|planned|program|source|architecture)\b/.test(normalized)) return "sky";
  if (/\b(segment|territory|module|view|data foundation)\b/.test(normalized)) return "violet";
  return "cyan";
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
