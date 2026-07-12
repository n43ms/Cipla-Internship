import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { DoctorDetailResponse, DoctorRoiResponse, DoctorRoiRow } from "../../types/api";
import { KpiCard } from "../common/DataStateComponents";
import { money } from "../budget/BudgetComponents";
import { CHART_AXIS_TICK, CHART_GRID_PROPS, CHART_TOOLTIP_CURSOR, CHART_TOOLTIP_PROPS, ChartLegendPills, compactChartValue } from "../common/ChartTheme";
import { TableLoadingOverlay } from "../common/TableLoadingOverlay";
import { SortableHeader, type SortState } from "../common/SortableTable";
import { WarningRegistration } from "../common/WarningCenter";
import { formatTitleText } from "../../utils/textFormat";

export type DoctorRoiSortKey = "doctorName" | "roiSegment" | "quadrantLabel" | "engagementCount" | "rcpaLastMonth" | "totalRoiSpendUsd" | "ciplaPrescriptionQty";

export function DoctorRoiCards({ data }: { data: DoctorRoiResponse }) {
  const showNoRcpa = data.noRcpaCount > 0;
  return (
    <div className={`grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 ${showNoRcpa ? "xl:grid-cols-4" : "xl:grid-cols-3"}`}>
      <KpiCard label="Doctor ROI rows" value={data.total} detail="Country-scoped P-code universe" />
      <KpiCard label="Dark-horse rows" value={data.darkHorseCount} detail="Unengaged Low Effort / High Reward" />
      {showNoRcpa ? <KpiCard label="No RCPA rows" value={data.noRcpaCount} detail="Engagement exists without prescription coverage" /> : null}
      <KpiCard label="Segments" value={Object.keys(data.segmentCounts).length} detail="Deterministic ROI buckets" />
    </div>
  );
}

const QUADRANT_TONE: Record<string, { card: string; label: string; value: string; dot: string; point: string }> = {
  "low effort / high reward": {
    card: "border-white/[0.08] bg-emerald-300/[0.045]",
    label: "text-emerald-200",
    value: "text-emerald-50",
    dot: "bg-emerald-300",
    point: "#6ee7b7",
  },
  "high effort / high reward": {
    card: "border-white/[0.08] bg-sky-300/[0.045]",
    label: "text-sky-200",
    value: "text-sky-50",
    dot: "bg-sky-300",
    point: "#67e8f9",
  },
  "low effort / low reward": {
    card: "border-white/[0.08] bg-white/[0.025]",
    label: "text-zinc-300",
    value: "text-zinc-50",
    dot: "bg-zinc-400",
    point: "#94a3b8",
  },
  "high effort / low reward": {
    card: "border-white/[0.08] bg-amber-300/[0.035]",
    label: "text-amber-200",
    value: "text-amber-50",
    dot: "bg-amber-300",
    point: "#fcd34d",
  },
};

const QUADRANT_ORDER = [
  "low effort / high reward",
  "high effort / high reward",
  "low effort / low reward",
  "high effort / low reward",
];

export function DoctorOpportunityChart({ rows }: { rows: DoctorRoiRow[] }) {
  const chartRows = [...rows]
    .sort((a, b) => b.ciplaPrescriptionQty - a.ciplaPrescriptionQty || a.totalRoiSpendUsd - b.totalRoiSpendUsd)
    .slice(0, 50)
    .map((row, index) => ({
      ...row,
      rank: index + 1,
      tone: QUADRANT_TONE[row.quadrantLabel],
    }));
  return (
    <div className="dashboard-card flex h-full min-h-[31rem] flex-col p-4">
      <div>
        <h2 className="font-semibold text-zinc-50">Top 50 doctor opportunity distribution</h2>
        <p className="mt-1 text-xs text-zinc-500">Bars rank doctors by Cipla Rx; color follows ROI quadrant.</p>
        <ChartLegendPills
          items={QUADRANT_ORDER.map((label) => ({
            label: formatQuadrantLabel(label),
            color: QUADRANT_TONE[label].point,
          }))}
        />
      </div>
      <div className="chart-frame mt-3 min-h-0 flex-1">
        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={280} debounce={100}>
          <BarChart data={chartRows} margin={{ top: 12, right: 20, bottom: 18, left: 4 }} barCategoryGap="10%">
            <CartesianGrid {...CHART_GRID_PROPS} vertical={false} />
            <XAxis
              dataKey="rank"
              tickFormatter={(value) => (Number(value) % 10 === 0 || Number(value) === 1 ? String(value) : "")}
              interval={0}
              tick={CHART_AXIS_TICK}
              axisLine={{ stroke: "rgba(161,161,170,0.18)" }}
              tickLine={false}
            />
            <YAxis
              type="number"
              dataKey="ciplaPrescriptionQty"
              name="Cipla Rx"
              tickFormatter={(value) => compactChartValue(value as number)}
              width={68}
              tick={CHART_AXIS_TICK}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              {...CHART_TOOLTIP_PROPS}
              cursor={CHART_TOOLTIP_CURSOR}
              formatter={(value) => {
                return [Number(value).toLocaleString(), "Cipla Rx"];
              }}
              labelFormatter={(_, payload) => {
                const row = payload?.[0]?.payload as (DoctorRoiRow & { rank: number }) | undefined;
                return row ? `#${row.rank} ${row.doctorName ?? row.pcodeNormalized} | ${money(row.totalRoiSpendUsd, "USD")} spend` : "Doctor";
              }}
            />
            <Bar name="Doctors" dataKey="ciplaPrescriptionQty" radius={[5, 5, 0, 0]} maxBarSize={10} isAnimationActive={false}>
              {chartRows.map((row) => <Cell key={`${row.countryCode}-${row.pcodeNormalized}`} fill={row.tone?.point ?? "#67e8f9"} opacity={0.92} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function QuadrantMatrix({ counts }: { counts: Record<string, number> }) {
  const insufficientDataCount = counts["insufficient data"] ?? 0;
  return (
    <div className="dashboard-card flex h-full min-h-[31rem] flex-col p-4">
      <h2 className="font-semibold text-zinc-50">ROI quadrant matrix</h2>
      <p className="mt-1 text-xs leading-5 text-zinc-500">
        Quadrants rank doctors by effort and reward. Effort is driven by investment and engagement intensity, while reward is driven by Cipla prescription opportunity. Low Effort / High Reward is the priority opportunity bucket.
      </p>
      <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
        {QUADRANT_ORDER.map((label) => {
          const tone = QUADRANT_TONE[label];
          return (
            <div key={label} className={`rounded-lg border p-3 ${tone.card}`}>
              <p className={`text-sm font-semibold ${tone.label}`}>{formatQuadrantLabel(label)}</p>
              <p className={`mt-2 text-2xl font-semibold ${tone.value}`}>{counts[label] ?? 0}</p>
            </div>
          );
        })}
      </div>
      {insufficientDataCount ? (
        <div className="mt-3 rounded-lg border border-amber-300/15 bg-amber-300/[0.045] p-3 text-xs leading-5 text-amber-100/85">
          Data warning: {insufficientDataCount.toLocaleString()} doctors are excluded from the matrix because spend, engagement, or RCPA evidence is insufficient for a stable ROI quadrant.
        </div>
      ) : null}
    </div>
  );
}

export function DoctorRoiTable({
  rows,
  page,
  pageSize,
  total,
  sort,
  isFetching = false,
  doctorSearch,
  onPageChange,
  onSelect,
  onSort,
  onDoctorSearchChange,
  onDoctorSearchSubmit,
}: {
  rows: DoctorRoiRow[];
  page: number;
  pageSize: number;
  total: number;
  sort: SortState<DoctorRoiSortKey>;
  isFetching?: boolean;
  doctorSearch: string;
  onPageChange: (page: number) => void;
  onSelect: (row: DoctorRoiRow) => void;
  onSort: (column: DoctorRoiSortKey) => void;
  onDoctorSearchChange: (value: string) => void;
  onDoctorSearchSubmit: () => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return (
    <div className="dashboard-card relative overflow-hidden">
      <TableLoadingOverlay isFetching={isFetching} label="Refreshing doctor rows" />
      <div className="flex flex-col gap-3 border-b border-zinc-800 p-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="font-semibold text-zinc-50">Doctor opportunities</h2>
          <p className="text-sm text-zinc-500">Showing {rows.length} of {total} rows. Sort columns to change the ROI view.</p>
        </div>
        <form
          className="grid gap-1 text-sm md:w-96"
          onSubmit={(event) => {
            event.preventDefault();
            onDoctorSearchSubmit();
          }}
        >
          <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">Search doctor</span>
          <div className="flex gap-2">
            <input
              className="form-control min-w-0 flex-1"
              value={doctorSearch}
              placeholder="Name or P-code"
              onChange={(event) => onDoctorSearchChange(event.target.value)}
            />
            <button type="submit" className="soft-button rounded-md border border-zinc-800 px-3 py-2 text-sm font-semibold text-zinc-200">Search</button>
          </div>
        </form>
      </div>
      <div className="table-scroll">
        <table className="min-w-full text-left text-sm">
          <thead className="table-head">
            <tr>
              <SortableHeader column="doctorName" label="Doctor" sort={sort} onSort={onSort} />
              <SortableHeader column="roiSegment" label="Segment" sort={sort} onSort={onSort} />
              <SortableHeader column="quadrantLabel" label="Quadrant" sort={sort} onSort={onSort} />
              <SortableHeader column="engagementCount" label="Engagements" sort={sort} onSort={onSort} />
              <SortableHeader column="rcpaLastMonth" label="RCPA baseline" sort={sort} onSort={onSort} />
              <SortableHeader column="totalRoiSpendUsd" label="Spend" sort={sort} onSort={onSort} />
              <SortableHeader column="ciplaPrescriptionQty" label="Cipla Rx" sort={sort} onSort={onSort} />
              <th className="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800">
            {rows.map((row) => (
              <tr key={`${row.countryCode}-${row.pcodeNormalized}`}>
                <td className="max-w-[16rem] px-4 py-3">
                  <p className="truncate font-medium text-zinc-100">{row.doctorName ?? "Unknown doctor"}</p>
                  <p className="text-xs text-zinc-500">{row.countryCode} - {row.pcodeNormalized}</p>
                </td>
                <td className="px-4 py-3">
                  {formatRoiSegment(row.roiSegment)}
                  {row.sponsorshipCount > 0 ? <span className="ml-2 rounded-full bg-sky-400/10 px-2 py-1 text-xs text-sky-300">Sponsored</span> : null}
                  {row.paidEngagementCount > 0 ? <span className="ml-2 rounded-full bg-violet-400/10 px-2 py-1 text-xs text-violet-300">Paid engagement</span> : null}
                  {row.noFeeEngagementCount > 0 ? <span className="ml-2 rounded-full bg-zinc-500/10 px-2 py-1 text-xs text-zinc-300">No-fee</span> : null}
                  {row.sponsorshipEngagementAmountMissingCount > 0 ? <span className="ml-2 rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">Amount unavailable</span> : null}
                  {row.darkHorseUnengagedFlag ? <span className="ml-2 rounded-full bg-emerald-400/10 px-2 py-1 text-xs text-emerald-300">Unengaged opportunity</span> : null}
                  {row.highValueEngagedFlag ? <span className="ml-2 rounded-full bg-cyan-400/10 px-2 py-1 text-xs text-cyan-300">Engaged value</span> : null}
                  {!row.hasRcpa ? <span className="ml-2 rounded-full bg-amber-400/10 px-2 py-1 text-xs text-amber-300">No RCPA</span> : null}
                </td>
                <td className="px-4 py-3">{formatQuadrantLabel(row.quadrantLabel)}</td>
                <td className="px-4 py-3">{row.engagementCount}</td>
                <td className="px-4 py-3 text-xs text-zinc-400">{rcpaPeriod(row)}</td>
                <td className="px-4 py-3">
                  {money(row.totalRoiSpendUsd, "USD")}
                  {row.totalRoiSpendUsd === 0 && row.sponsorshipCount === 0 && row.paidEngagementCount === 0 ? <p className="text-xs text-zinc-500">True zero evidence</p> : null}
                  {row.totalRoiSpendUsd === 0 && row.sponsorshipEngagementAmountMissingCount > 0 ? <p className="text-xs text-amber-300">Prior evidence, amount unavailable</p> : null}
                </td>
                <td className="px-4 py-3">{row.ciplaPrescriptionQty.toLocaleString()}</td>
                <td className="px-4 py-3">
                  <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 text-xs" onClick={() => onSelect(row)}>Open</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-zinc-800 p-4 text-sm">
        <span className="text-zinc-500">Page {page} of {totalPages}</span>
        <div className="flex gap-2">
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button>
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}

export function DoctorOutcomeEvidence({ detail }: { detail: DoctorDetailResponse }) {
  const outcome = detail.sponsorshipOutcome;
  if (!outcome) {
    const engagementCount = detail.engagementHistory.length;
    return (
      <section>
        <h3 className="font-semibold">Sponsorship and engagement evidence</h3>
        <p className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-2 text-zinc-500">
          {engagementCount > 0
            ? `No sponsorship outcome summary is available, but ${engagementCount.toLocaleString()} engagement record${engagementCount === 1 ? "" : "s"} appear below.`
            : "No sponsorship outcome summary or engagement history is available for this doctor."}
        </p>
      </section>
    );
  }
  return (
    <>
      {outcome.evidenceCaveats.length ? (
        <WarningRegistration
          record={{
            id: `doctor-outcome-${detail.profile.countryCode}-${detail.profile.pcodeNormalized}`,
            title: "Doctor drilldown evidence notes",
            tone: "warning",
            items: outcome.evidenceCaveats.map((caveat) => formatTitleText(caveat)),
          }}
        />
      ) : null}
      <section className="grid gap-3">
      <div>
        <h3 className="font-semibold">Sponsorship and engagement evidence</h3>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <EvidenceMetric label="Sponsorships" value={outcome.sponsorshipCount.toLocaleString()} />
        <EvidenceMetric label="Paid engagements" value={outcome.paidEngagementCount.toLocaleString()} />
        <EvidenceMetric label="No-fee history" value={outcome.noFeeEngagementCount.toLocaleString()} />
        <EvidenceMetric label="Contracted" value={money(outcome.contractedAmountUsd, "USD")} />
        <EvidenceMetric label="FMV" value={money(outcome.fmvAmountUsd, "USD")} />
        <EvidenceMetric label="Saving" value={money(outcome.contractSavingUsd, "USD")} />
        <EvidenceMetric label="Known investment" value={money(outcome.knownEngagementInvestmentUsd, "USD")} />
      </div>
    </section>
    </>
  );
}

function EvidenceMetric({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-2">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 break-words font-semibold text-zinc-100">{value}</p>
      {detail ? <p className="text-xs text-zinc-500">{detail}</p> : null}
    </div>
  );
}

function rcpaPeriod(row: DoctorRoiRow) {
  if (!row.hasRcpa) return "No RCPA baseline";
  if (!row.rcpaFirstMonth || !row.rcpaLastMonth) return "Baseline period unknown";
  return `${formatMonth(row.rcpaFirstMonth)} to ${formatMonth(row.rcpaLastMonth)}`;
}

function formatMonth(value: string) {
  return new Date(value).toLocaleDateString(undefined, { month: "short", year: "numeric" });
}

export function formatRoiSegment(value: string | null | undefined) {
  if (!value) return "Segment Unavailable";
  const known: Record<string, string> = {
    high_value_unengaged: "High-Value Unengaged",
    high_value_engaged: "High-Value Engaged",
    low_value_unengaged: "Low-Value Unengaged",
    low_value_engaged: "Low-Value Engaged",
    dark_horse: "Dark Horse",
    no_rcpa: "No RCPA",
    insufficient_data: "Insufficient Data",
  };
  return known[value] ?? formatTitleText(value);
}

export function formatQuadrantLabel(value: string | null | undefined) {
  if (!value) return "Quadrant Unavailable";
  const known: Record<string, string> = {
    "low effort / high reward": "Low Effort / High Reward",
    "high effort / high reward": "High Effort / High Reward",
    "low effort / low reward": "Low Effort / Low Reward",
    "high effort / low reward": "High Effort / Low Reward",
    "insufficient data": "Insufficient Data",
  };
  return known[value] ?? formatTitleText(value);
}
