import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { getFilters } from "../api/filters";
import { getTerritoryDoctors, getTerritoryOpportunities } from "../api/territory";
import { CHART_COLORS, CHART_TOOLTIP_PROPS, ChartLegendPills } from "../components/common/ChartTheme";
import { DataFreshnessBanner, EmptyState, ErrorState, KpiCard, LoadingState } from "../components/common/DataStateComponents";
import { SidePanel } from "../components/common/SidePanel";
import { SmoothSelect } from "../components/common/SmoothSelect";
import { TableLoadingOverlay } from "../components/common/TableLoadingOverlay";
import { WarningRegistration } from "../components/common/WarningCenter";
import { nextSort, SortableHeader, type SortState } from "../components/common/SortableTable";
import { formatTitleText } from "../utils/textFormat";
import type { TerritoryOpportunityRow } from "../types/api";

const LABEL_OPTIONS = [
  { value: "underserved", label: "Underserved" },
  { value: "overserved", label: "Overserved" },
  { value: "balanced", label: "Balanced" },
  { value: "insufficient_data", label: "Insufficient Data" },
];

const SIGNAL_SORT_RANK: Record<string, number> = {
  underserved: 0,
  overserved: 1,
  balanced: 2,
  insufficient_data: 3,
};

const SIGNAL_TONE: Record<string, { color: string; textClass: string }> = {
  underserved: { color: CHART_COLORS.amber, textClass: "text-amber-100" },
  overserved: { color: CHART_COLORS.rose, textClass: "text-rose-100" },
  balanced: { color: CHART_COLORS.emerald, textClass: "text-emerald-100" },
  insufficient_data: { color: CHART_COLORS.zinc, textClass: "text-zinc-300" },
};

type TerritorySortKey = "territoryName" | "opportunityLabel" | "doctorCount" | "totalPrescriptionQty";

export function TerritoryIntelligence({ onAiContextChange }: { onAiContextChange?: (context: { pageContext: string; filters: Record<string, unknown> }) => void }) {
  const [country, setCountry] = useState("");
  const [opportunityLabel, setOpportunityLabel] = useState("");
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<SortState<TerritorySortKey>>({ key: "totalPrescriptionQty", direction: "desc" });
  const [selectedTerritory, setSelectedTerritory] = useState<TerritoryOpportunityRow | null>(null);
  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const query = useQuery({
    queryKey: ["territory-opportunities", country, opportunityLabel, page, sort.key, sort.direction],
    queryFn: () => getTerritoryOpportunities({ country, opportunityLabel, page, pageSize: 25, sortBy: sort.key, sortDir: sort.direction }),
    placeholderData: (previousData) => previousData,
  });
  const territoryDoctors = useQuery({
    queryKey: ["territory-doctors", selectedTerritory?.countryCode, selectedTerritory?.territoryName, selectedTerritory?.patchName],
    queryFn: () => getTerritoryDoctors({
      country: selectedTerritory!.countryCode,
      territoryName: selectedTerritory!.territoryName,
      patchName: selectedTerritory!.patchName,
    }),
    enabled: Boolean(selectedTerritory),
  });
  const aiFilters = useMemo(
    () => ({ country: country || undefined, opportunityLabel: opportunityLabel || undefined }),
    [country, opportunityLabel],
  );
  const territoryWarningItems = useMemo(
    () => buildTerritoryWarningItems(query.data?.rows ?? [], query.data?.meta.limitations ?? []),
    [query.data?.rows, query.data?.meta.limitations],
  );
  const sortedRows = useMemo(
    () => sortTerritoryRows(query.data?.rows ?? [], sort),
    [query.data?.rows, sort],
  );

  useEffect(() => {
    onAiContextChange?.({ pageContext: "territory", filters: aiFilters });
  }, [aiFilters, onAiContextChange]);

  function handleSort(column: TerritorySortKey) {
    setSort((current) => nextSort(current, column));
    setPage(1);
  }

  if (query.isLoading && !query.data) return <main><LoadingState label="Loading territory intelligence" /></main>;
  if (query.isError) return <main className="p-6"><ErrorState title="Territory intelligence unavailable" /></main>;
  if (!query.data) return null;

  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Territory intelligence</p>
          <h1 className="page-title">Territory opportunity signals</h1>
          <p className="page-copy">
            Uses source-backed RCPA territory, patch, and engagement HQ fields to flag underserved, overserved, and balanced territory patterns.
          </p>
        </header>
        <DataFreshnessBanner meta={query.data.meta} />
        <section className="dashboard-card relative z-40 overflow-visible p-4">
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
            items: territoryWarningItems,
          }}
        />
        <TerritoryCards total={query.data.total} labelCounts={query.data.labelCounts} />
        <TerritorySignalPie labelCounts={query.data.labelCounts} />
        {query.data.rows.length ? (
          <section className="dashboard-card relative overflow-hidden p-0">
            <TableLoadingOverlay isFetching={query.isFetching} label="Refreshing territory rows" />
            <div className="overflow-x-auto">
              <table className="min-w-full table-fixed text-left text-sm">
                <colgroup>
                  <col className="w-[36%]" />
                  <col className="w-[20%]" />
                  <col className="w-[14%]" />
                  <col className="w-[14%]" />
                  <col className="w-40" />
                </colgroup>
                <thead className="border-b border-zinc-800 text-xs uppercase tracking-wide text-zinc-500">
                  <tr>
                    <SortableHeader column="territoryName" label="Territory" sort={sort} onSort={handleSort} />
                    <SortableHeader column="opportunityLabel" label="Signal" sort={sort} onSort={handleSort} />
                    <SortableHeader column="doctorCount" label="Doctors" sort={sort} onSort={handleSort} />
                    <SortableHeader column="totalPrescriptionQty" label="Rx" sort={sort} onSort={handleSort} />
                    <th className="px-4 py-3 text-center">Doctor drilldown</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRows.map((row) => (
                    <TerritoryRow key={`${row.countryCode}-${row.territoryName}-${row.patchName ?? ""}`} row={row} onOpenDoctors={setSelectedTerritory} />
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
          <EmptyState title="No source-backed territory rows" detail="Territory signals appear after RCPA Location/Patch Name or engagement FS HQ fields are loaded into Supabase." />
        )}
      </div>
      <SidePanel open={Boolean(selectedTerritory)} onClose={() => setSelectedTerritory(null)} widthClass="max-w-md">
        {selectedTerritory ? (
          <TerritoryDoctorsPanel
            isError={territoryDoctors.isError}
            isLoading={territoryDoctors.isLoading}
            rows={territoryDoctors.data?.rows ?? []}
            territory={selectedTerritory}
          />
        ) : null}
      </SidePanel>
    </main>
  );
}

function TerritoryCards({ total, labelCounts }: { total: number; labelCounts: Record<string, number> }) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Metric tone="violet" title="Territories" value={total.toLocaleString()} detail="Current filtered total" />
      <Metric tone="amber" title="Underserved" value={String(labelCounts.underserved ?? 0)} detail="High Rx with no engagement evidence" />
      <Metric tone="red" title="Overserved" value={String(labelCounts.overserved ?? 0)} detail="Spend or engagement exceeds current Rx signal" />
      <Metric tone="emerald" title="Balanced" value={String(labelCounts.balanced ?? 0)} detail="No exception signal from current evidence" />
    </section>
  );
}

function TerritorySignalPie({ labelCounts }: { labelCounts: Record<string, number> }) {
  const rows = LABEL_OPTIONS
    .map((option) => ({
      key: option.value,
      label: option.label,
      value: labelCounts[option.value] ?? 0,
      color: SIGNAL_TONE[option.value]?.color ?? CHART_COLORS.cyan,
    }))
    .filter((row) => row.value > 0);
  if (!rows.length) return null;
  return (
    <section className="dashboard-card p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="font-semibold text-zinc-50">Territory signal mix</h2>
          <p className="mt-1 text-sm text-zinc-500">Share of territory signals in the current filtered scope.</p>
          <ChartLegendPills items={rows.map((row) => ({ label: row.label, color: row.color, detail: row.value.toLocaleString() }))} />
        </div>
        <div className="chart-frame h-fit min-w-0 -my-3">
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={150} debounce={100}>
            <PieChart>
              <Tooltip {...CHART_TOOLTIP_PROPS} formatter={(value) => Number(value).toLocaleString()} />
              <Pie data={rows} dataKey="value" nameKey="label" innerRadius={45} outerRadius={70} paddingAngle={1} stroke="rgba(13,17,19,0.86)" strokeWidth={2}>
                {rows.map((row) => (
                  <Cell key={row.key} fill={row.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

function TerritoryRow({ row, onOpenDoctors }: { row: TerritoryOpportunityRow; onOpenDoctors: (row: TerritoryOpportunityRow) => void }) {
  return (
    <tr className="border-b border-zinc-900/80 align-top">
      <td className="px-4 py-3">
        <p className="font-medium text-zinc-100">{row.territoryName}</p>
        <p className="text-xs text-zinc-500">{row.countryName}</p>
      </td>
      <td className="px-4 py-3">
        <span className={`text-sm font-medium ${signalTextClass(row.opportunityLabel)}`}>{formatSignalLabel(row.opportunityLabel)}</span>
      </td>
      <td className="px-4 py-3 text-zinc-300">{row.doctorCount.toLocaleString()}</td>
      <td className="px-4 py-3 text-zinc-300">{row.totalPrescriptionQty.toLocaleString()}</td>
      <td className="px-4 py-3 text-center">
        <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 text-xs" onClick={() => onOpenDoctors(row)}>Open</button>
      </td>
    </tr>
  );
}

function TerritoryDoctorsPanel({
  isError,
  isLoading,
  rows,
  territory,
}: {
  isError: boolean;
  isLoading: boolean;
  rows: Array<{ doctorName: string; pcodeNormalized: string }>;
  territory: TerritoryOpportunityRow;
}) {
  return (
    <div className="space-y-4">
      <header className="border-b border-zinc-800 pb-4">
        <p className="text-xs font-medium uppercase tracking-wide text-accent">Territory doctors</p>
        <h2 className="mt-2 break-words text-2xl font-semibold">{territory.territoryName}</h2>
      </header>
      {isLoading ? <LoadingState label="Loading territory doctors" compact /> : null}
      {isError ? <p className="text-sm text-amber-100/85">Doctor list unavailable.</p> : null}
      {!isLoading && !isError && rows.length === 0 ? <p className="text-sm text-muted">No doctors found for this territory.</p> : null}
      {!isLoading && !isError && rows.length ? (
        <div className="grid gap-2">
          {rows.map((doctor) => (
            <p key={doctor.pcodeNormalized} className="rounded-md border border-zinc-800 bg-zinc-900 p-3 text-sm text-zinc-100">
              {doctor.doctorName} ({doctor.pcodeNormalized})
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function Metric({ title, value, detail, tone }: { title: string; value: string; detail: string; tone: "cyan" | "sky" | "emerald" | "amber" | "red" | "violet" }) {
  return <KpiCard tone={tone} label={title} value={value} detail={detail} />;
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

function buildTerritoryWarningItems(rows: TerritoryOpportunityRow[], limitations: string[]) {
  const confidenceCounts = rows.reduce<Record<string, number>>((counts, row) => {
    const key = row.evidenceConfidence || "unknown";
    counts[key] = (counts[key] ?? 0) + 1;
    return counts;
  }, {});
  const confidenceSummary = Object.entries(confidenceCounts)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([confidence, count]) => `${formatConfidence(confidence)} confidence: ${count.toLocaleString()} territories`)
    .join("; ");
  const caveatCounts = rows.reduce<Record<string, number>>((counts, row) => {
    row.sourceCaveats.forEach((caveat) => {
      const normalized = formatTitleText(caveat);
      counts[normalized] = (counts[normalized] ?? 0) + 1;
    });
    return counts;
  }, {});
  const caveatSummaries = Object.entries(caveatCounts)
    .sort(([, a], [, b]) => b - a)
    .map(([caveat, count]) => `${caveat}: ${count.toLocaleString()} territories`);
  return [
    ...limitations,
    confidenceSummary ? `Evidence confidence distribution in current view: ${confidenceSummary}.` : "",
    ...caveatSummaries,
  ];
}

function sortTerritoryRows(rows: TerritoryOpportunityRow[], sort: SortState<TerritorySortKey>) {
  const multiplier = sort.direction === "asc" ? 1 : -1;
  return [...rows].sort((left, right) => multiplier * compareTerritoryValue(territorySortValue(left, sort.key), territorySortValue(right, sort.key)));
}

function territorySortValue(row: TerritoryOpportunityRow, key: TerritorySortKey) {
  if (key === "opportunityLabel") return SIGNAL_SORT_RANK[normalizeSignalKey(row.opportunityLabel)] ?? 99;
  return row[key];
}

function compareTerritoryValue(left: string | number, right: string | number) {
  if (typeof left === "number" && typeof right === "number") return left - right;
  return String(left).localeCompare(String(right), undefined, { numeric: true, sensitivity: "base" });
}

function formatConfidence(value: string) {
  return formatTitleText(value);
}

function formatSignalLabel(value: string) {
  return LABEL_OPTIONS.find((option) => option.value === normalizeSignalKey(value))?.label ?? formatConfidence(value);
}

function signalTextClass(value: string) {
  return SIGNAL_TONE[normalizeSignalKey(value)]?.textClass ?? "text-zinc-200";
}

function normalizeSignalKey(value: string) {
  return value.trim().toLowerCase().replaceAll(" ", "_").replaceAll("-", "_");
}
