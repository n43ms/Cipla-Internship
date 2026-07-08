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

export function KpiCard({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return (
    <div className="dashboard-card p-4">
      <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-zinc-50">{value}</p>
      {detail ? <p className="mt-1 text-xs text-zinc-500">{detail}</p> : null}
    </div>
  );
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
