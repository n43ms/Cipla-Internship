import type { ResponseMeta } from "../../types/api";

export function DataFreshnessBanner({ meta }: { meta?: ResponseMeta }) {
  if (!meta) return null;
  const hasWarnings = meta.dataQualityFlags.length > 0 || meta.limitations.length > 0;
  return (
    <section className={`dashboard-card p-4 ${hasWarnings ? "border-amber-300 bg-amber-50" : "border-emerald-200 bg-emerald-50"}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Data freshness</p>
          <p className="text-sm text-slate-800">Latest ingestion status: <strong>{meta.latestIngestionStatus}</strong></p>
        </div>
        <p className="text-xs text-slate-500">Generated {new Date(meta.generatedAt).toLocaleString()}</p>
      </div>
      {hasWarnings ? <LimitationList limitations={[...meta.dataQualityFlags, ...meta.limitations]} /> : null}
    </section>
  );
}

export function LimitationList({ limitations }: { limitations: string[] }) {
  const unique = Array.from(new Set(limitations)).filter(Boolean);
  if (!unique.length) return null;
  return (
    <ul className="mt-3 grid gap-1 text-xs text-amber-900 sm:grid-cols-2">
      {unique.map((item) => (
        <li key={item} className="rounded-md bg-white/70 px-2 py-1">{humanize(item)}</li>
      ))}
    </ul>
  );
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="dashboard-card p-6 text-center">
      <p className="font-semibold text-slate-800">{title}</p>
      <p className="mt-1 text-sm text-slate-500">{detail}</p>
    </div>
  );
}

export function ErrorState({ title = "Dashboard data unavailable" }: { title?: string }) {
  return (
    <div className="dashboard-card border-red-200 bg-red-50 p-6">
      <p className="font-semibold text-red-900">{title}</p>
      <p className="mt-1 text-sm text-red-700">The backend could not return this API. Check the server logs and migration state.</p>
    </div>
  );
}

export function KpiCard({ label, value, detail }: { label: string; value: string | number; detail?: string }) {
  return (
    <div className="dashboard-card p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
      {detail ? <p className="mt-1 text-xs text-slate-500">{detail}</p> : null}
    </div>
  );
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
