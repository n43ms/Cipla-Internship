import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getFilters } from "../api/filters";
import { getTerritoryOpportunities } from "../api/territory";
import { DataFreshnessBanner, EmptyState, ErrorState, LoadingState } from "../components/common/DataStateComponents";
import { SmoothSelect } from "../components/common/SmoothSelect";
import { TableLoadingOverlay } from "../components/common/TableLoadingOverlay";
import { WarningRegistration } from "../components/common/WarningCenter";
import type { TerritoryOpportunityRow } from "../types/api";

const LABEL_OPTIONS = [
  { value: "underserved", label: "Underserved" },
  { value: "overserved", label: "Overserved" },
  { value: "self_serving", label: "Self-serving" },
  { value: "balanced", label: "Balanced" },
  { value: "insufficient_data", label: "Insufficient data" },
];

export function TerritoryIntelligence({ onAiContextChange }: { onAiContextChange?: (context: { pageContext: string; filters: Record<string, unknown> }) => void }) {
  const [country, setCountry] = useState("");
  const [opportunityLabel, setOpportunityLabel] = useState("");
  const [page, setPage] = useState(1);
  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const query = useQuery({
    queryKey: ["territory-opportunities", country, opportunityLabel, page],
    queryFn: () => getTerritoryOpportunities({ country, opportunityLabel, page, pageSize: 25 }),
    placeholderData: (previousData) => previousData,
  });
  const aiFilters = useMemo(
    () => ({ country: country || undefined, opportunityLabel: opportunityLabel || undefined }),
    [country, opportunityLabel],
  );

  useEffect(() => {
    onAiContextChange?.({ pageContext: "territory", filters: aiFilters });
  }, [aiFilters, onAiContextChange]);

  if (query.isLoading && !query.data) return <main><LoadingState label="Loading territory intelligence" /></main>;
  if (query.isError) return <main className="p-6"><ErrorState title="Territory intelligence unavailable" /></main>;
  if (!query.data) return null;

  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Territory Intelligence</p>
          <h1 className="page-title">Territory opportunity signals</h1>
          <p className="page-copy">
            Uses source-backed RCPA territory/patch and engagement HQ fields to flag underserved, overserved, and transactional territory patterns.
          </p>
        </header>
        <DataFreshnessBanner meta={query.data.meta} />
        <section className="dashboard-card overflow-visible p-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <Select label="Country" value={country} options={filters.data?.countries ?? []} empty="All countries" onChange={(value) => { setCountry(value); setPage(1); }} />
            <Select label="Signal" value={opportunityLabel} options={LABEL_OPTIONS} empty="All signals" onChange={(value) => { setOpportunityLabel(value); setPage(1); }} />
            <button className="soft-button self-end rounded-md border border-zinc-800 px-4 py-2 text-sm" onClick={() => { setCountry(""); setOpportunityLabel(""); setPage(1); }}>Clear</button>
          </div>
        </section>
        <WarningRegistration
          record={{
            id: "territory-intelligence-notes",
            title: "Territory intelligence notes",
            tone: "info",
            items: query.data.meta.limitations,
          }}
        />
        <TerritoryCards rows={query.data.rows} labelCounts={query.data.labelCounts} />
        {query.data.rows.length ? (
          <section className="dashboard-card relative overflow-hidden p-0">
            <TableLoadingOverlay isFetching={query.isFetching} label="Refreshing territory rows" />
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="border-b border-zinc-800 text-xs uppercase tracking-wide text-zinc-500">
                  <tr>
                    <th className="px-4 py-3">Territory</th>
                    <th className="px-4 py-3">Signal</th>
                    <th className="px-4 py-3">Doctors</th>
                    <th className="px-4 py-3">Rx</th>
                    <th className="px-4 py-3">Engagements</th>
                    <th className="px-4 py-3">Known investment</th>
                    <th className="px-4 py-3">Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {query.data.rows.map((row) => (
                    <TerritoryRow key={`${row.countryCode}-${row.territoryName}-${row.patchName ?? ""}`} row={row} />
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between border-t border-zinc-800 px-4 py-3 text-sm text-zinc-400">
              <span>Showing {query.data.rows.length} of {query.data.total}</span>
              <div className="flex gap-2">
                <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-40" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Previous</button>
                <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-40" disabled={page * query.data.pageSize >= query.data.total} onClick={() => setPage((value) => value + 1)}>Next</button>
              </div>
            </div>
          </section>
        ) : (
          <EmptyState title="No source-backed territory rows" detail="Territory signals appear after RCPA Location/PATCHNAME or engagement FS HQ fields are loaded into Supabase." />
        )}
      </div>
    </main>
  );
}

function TerritoryCards({ rows, labelCounts }: { rows: TerritoryOpportunityRow[]; labelCounts: Record<string, number> }) {
  const knownInvestment = rows.reduce((sum, row) => sum + row.knownInvestmentUsd, 0);
  const totalRx = rows.reduce((sum, row) => sum + row.totalPrescriptionQty, 0);
  return (
    <section className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <Metric title="Territories" value={String(rows.length)} detail="Current filtered rows" />
      <Metric title="Underserved" value={String(labelCounts.underserved ?? 0)} detail="High Rx with no engagement evidence" />
      <Metric title="Overserved" value={String(labelCounts.overserved ?? 0)} detail="Spend/engagement exceeds current Rx signal" />
      <Metric title="Known investment" value={`$${knownInvestment.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} detail={`${totalRx.toLocaleString()} total Rx in view`} />
    </section>
  );
}

function TerritoryRow({ row }: { row: TerritoryOpportunityRow }) {
  return (
    <tr className="border-b border-zinc-900/80 align-top">
      <td className="px-4 py-3">
        <p className="font-medium text-zinc-100">{row.territoryName}</p>
        <p className="text-xs text-zinc-500">{row.countryName}{row.patchName ? ` - ${row.patchName}` : ""}</p>
      </td>
      <td className="px-4 py-3">
        <span className="rounded-md border border-accent/20 bg-accent/[0.08] px-2 py-1 text-xs text-cyan-100">{row.opportunityLabel.replaceAll("_", " ")}</span>
        {row.sourceCaveats.length ? <p className="mt-2 text-xs text-amber-100/70">{row.sourceCaveats.join(", ")}</p> : null}
      </td>
      <td className="px-4 py-3 text-zinc-300">{row.doctorCount.toLocaleString()} total<br /><span className="text-xs text-zinc-500">{row.engagedDoctorCount.toLocaleString()} engaged</span></td>
      <td className="px-4 py-3 text-zinc-300">{row.totalPrescriptionQty.toLocaleString()}<br /><span className="text-xs text-zinc-500">{formatPercent(row.ciplaShareQty)} Cipla share</span></td>
      <td className="px-4 py-3 text-zinc-300">{row.engagementCount.toLocaleString()}<br /><span className="text-xs text-zinc-500">{row.sponsorshipCount} sponsored, {row.paidEngagementCount} paid</span></td>
      <td className="px-4 py-3 text-zinc-300">${row.knownInvestmentUsd.toLocaleString(undefined, { maximumFractionDigits: 0 })}<br /><span className="text-xs text-zinc-500">saving ${row.contractSavingUsd.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></td>
      <td className="px-4 py-3 text-zinc-300">{row.evidenceConfidence}</td>
    </tr>
  );
}

function Metric({ title, value, detail }: { title: string; value: string; detail: string }) {
  return (
    <div className="dashboard-card p-4">
      <p className="text-xs uppercase tracking-wide text-zinc-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-zinc-50">{value}</p>
      <p className="mt-1 text-xs text-zinc-500">{detail}</p>
    </div>
  );
}

function Select({
  label,
  value,
  options,
  empty,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  empty: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="grid gap-1 text-sm">
      <span className="font-medium text-zinc-300">{label}</span>
      <SmoothSelect ariaLabel={label} value={value} options={options} placeholder={empty} onChange={onChange} />
    </div>
  );
}

function formatPercent(value: number | null) {
  if (value == null) return "n/a";
  return `${Math.round(value * 100)}%`;
}
