import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getDoctorDetail, getDoctorRoi } from "../api/doctors";
import { getFilters } from "../api/filters";
import { DataFreshnessBanner, EmptyState, ErrorState, LoadingState } from "../components/common/DataStateComponents";
import { SidePanel } from "../components/common/SidePanel";
import { SmoothSelect } from "../components/common/SmoothSelect";
import { WarningRegistration } from "../components/common/WarningCenter";
import { DoctorOpportunityChart, DoctorOutcomeEvidence, DoctorRoiCards, DoctorRoiTable, QuadrantMatrix, formatRoiSegment, type DoctorRoiSortKey } from "../components/doctors/DoctorRoiComponents";
import { nextSort, type SortState } from "../components/common/SortableTable";
import type { DoctorRoiRow } from "../types/api";

export function DoctorRoi({ onAiContextChange }: { onAiContextChange?: (context: { pageContext: string; filters: Record<string, unknown> }) => void }) {
  const [selected, setSelected] = useState<DoctorRoiRow | null>(null);
  const [country, setCountry] = useState("");
  const [monthStart, setMonthStart] = useState("");
  const [monthEnd, setMonthEnd] = useState("");
  const [brand, setBrand] = useState("");
  const [speciality, setSpeciality] = useState("");
  const [doctorClass, setDoctorClass] = useState("");
  const [roiSegment, setRoiSegment] = useState("");
  const [includeOutOfScope, setIncludeOutOfScope] = useState(true);
  const [doctorSearchInput, setDoctorSearchInput] = useState("");
  const [doctorSearch, setDoctorSearch] = useState("");
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<SortState<DoctorRoiSortKey>>({ key: "ciplaPrescriptionQty", direction: "desc" });

  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const aiFilters = useMemo(
    () => ({
      country: country || undefined,
      month: monthEnd || monthStart || undefined,
      brand: brand || undefined,
      speciality: speciality || undefined,
      doctorClass: doctorClass || undefined,
      roiSegment: roiSegment || undefined,
      doctorSearch: doctorSearch || undefined,
      includeOutOfScope: includeOutOfScope || undefined,
    }),
    [brand, country, doctorClass, doctorSearch, includeOutOfScope, monthEnd, monthStart, roiSegment, speciality],
  );
  const roi = useQuery({
    queryKey: ["doctor-roi", country, monthStart, monthEnd, brand, speciality, doctorClass, roiSegment, doctorSearch, includeOutOfScope, page, sort],
    queryFn: () => getDoctorRoi({ country, monthStart, monthEnd, brand, speciality, doctorClass, roiSegment, doctorSearch, includeOutOfScope, page, pageSize: 50, sort: sort.key, sortDirection: sort.direction }),
    placeholderData: (previousData) => previousData,
  });

  useEffect(() => {
    onAiContextChange?.({ pageContext: "doctor_roi", filters: aiFilters });
  }, [aiFilters, onAiContextChange]);
  const detail = useQuery({
    queryKey: ["doctor-detail", selected?.countryCode, selected?.pcodeNormalized],
    queryFn: () => getDoctorDetail(selected!.countryCode, selected!.pcodeNormalized),
    enabled: Boolean(selected),
  });

  if (roi.isLoading && !roi.data) return <main><LoadingState label="Loading doctor ROI" /></main>;
  if (roi.isError) return <main className="p-6"><ErrorState title="Doctor ROI unavailable" /></main>;
  if (!roi.data) return null;

  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Doctor ROI</p>
          <h1 className="page-title">Doctor opportunities and missed value</h1>
          <p className="page-copy">
            Connects actual attended doctors to allocated spend and RCPA prescription behavior using country-scoped P-codes.
          </p>
        </header>
        <DataFreshnessBanner meta={roi.data.meta} />
        <section className="dashboard-card relative z-50 overflow-visible p-3">
          <div className="mb-3 flex flex-col items-center justify-center gap-2 border-b border-white/[0.06] pb-3 text-center sm:flex-row">
            <label className="flex items-center gap-2 rounded-md bg-white/[0.025] px-3 py-2 text-sm text-zinc-300">
              <input type="checkbox" checked={includeOutOfScope} onChange={(event) => { setIncludeOutOfScope(event.target.checked); setPage(1); }} />
              All loaded markets
            </label>
            <p className="text-xs text-zinc-500">{includeOutOfScope ? "Showing every loaded market." : "Restricted to Nepal and Sri Lanka primary-market scope."}</p>
          </div>
          <div className="grid grid-cols-1 items-end justify-items-stretch gap-2 overflow-visible pb-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
            <Select label="Country" value={country} options={filters.data?.countries ?? []} empty="All Countries" onChange={(value) => { setCountry(value); setPage(1); }} />
            <Select label="Start Month" value={monthStart} options={filters.data?.months ?? []} empty="Any Start" onChange={(value) => { setMonthStart(value); setPage(1); }} />
            <Select label="End Month" value={monthEnd} options={filters.data?.months ?? []} empty="Any End" onChange={(value) => { setMonthEnd(value); setPage(1); }} />
            <Select label="Brand Baseline" value={brand} options={filters.data?.brands ?? []} empty="All Brands" onChange={(value) => { setBrand(value); setPage(1); }} />
            <Select label="Specialty" value={speciality} options={filters.data?.specialities ?? []} empty="All specialties" onChange={(value) => { setSpeciality(value); setPage(1); }} />
            <Select label="Doctor Class" value={doctorClass} options={filters.data?.doctorClasses ?? []} empty="All Classes" onChange={(value) => { setDoctorClass(value); setPage(1); }} />
            <Select label="ROI Segment" value={roiSegment} options={formatRoiOptions(filters.data?.roiSegments ?? [])} empty="All Segments" onChange={(value) => { setRoiSegment(value); setPage(1); }} />
          </div>
          <div className="mt-2 flex justify-end">
            <button className="soft-button rounded-md border border-zinc-800 px-4 py-2 text-sm" onClick={() => { setCountry(""); setMonthStart(""); setMonthEnd(""); setBrand(""); setSpeciality(""); setDoctorClass(""); setRoiSegment(""); setDoctorSearchInput(""); setDoctorSearch(""); setIncludeOutOfScope(true); setPage(1); }}>Clear filters</button>
          </div>
        </section>
        <WarningRegistration
          record={{
            id: "doctor-roi-interpretation",
            title: "Doctor ROI interpretation notes",
            tone: "info",
            items: [
              "Doctor ROI now defaults to all loaded markets; turn off All loaded markets to restrict the view to Nepal and Sri Lanka primary markets.",
              "RCPA prescription data is a historical baseline.",
              "Brand filters identify doctors with that brand in baseline RCPA; displayed ROI metrics remain all-brand doctor totals.",
            ],
          }}
        />
        <DoctorRoiCards data={roi.data} />
        {roi.data?.rows?.length ? (
          <div className="grid min-w-0 grid-cols-1 items-stretch gap-5 xl:grid-cols-2">
            <DoctorOpportunityChart rows={roi.data.rows} />
            <QuadrantMatrix counts={roi.data?.quadrantCounts ?? {}} />
            <div className="xl:col-span-2">
              <DoctorRoiTable
                rows={roi.data.rows}
                page={page}
                pageSize={roi.data?.pageSize ?? 50}

                total={roi.data?.total ?? 0}

                sort={sort}
                isFetching={roi.isFetching}
                doctorSearch={doctorSearchInput}
                onPageChange={setPage}
                onSelect={setSelected}
                onSort={(column) => { setSort((current) => nextSort(current, column)); setPage(1); }}
                onDoctorSearchChange={setDoctorSearchInput}
                onDoctorSearchSubmit={() => { setDoctorSearch(doctorSearchInput.trim()); setPage(1); }}
              />
            </div>
          </div>
        ) : (
          <EmptyState title="No doctor ROI rows" detail="Doctor ROI needs actual attendance P-codes or RCPA summary rows." />
        )}
      </div>
      <SidePanel open={Boolean(selected)} onClose={() => setSelected(null)} widthClass="sm:max-w-xl">
        {selected ? <>
          <button className="soft-button rounded-md border border-zinc-800 px-3 py-1 text-sm" onClick={() => setSelected(null)}>Close</button>
          <h2 className="mt-4 break-words text-xl font-semibold">{selected.doctorName ?? selected.pcodeNormalized}</h2>
          <p className="break-words text-sm text-zinc-500">{selected.countryCode} - {formatSegment(selected.roiSegment)}</p>
          <div className="mt-3 grid gap-2 rounded-md border border-zinc-800 bg-zinc-950 p-3 text-xs text-zinc-400">
            <p>
              Territory: <span className="text-zinc-200">{selected.territoryName ?? "not mapped"}</span>
              {selected.territoryId ? <span className="text-zinc-500"> ({selected.territoryId})</span> : null}
            </p>
            <p>
              Doctor master:{" "}
              <span className={selected.hasDoctorMaster ? "text-emerald-300" : "text-zinc-500"}>
                {selected.hasDoctorMaster ? "MSL mapped" : "Not available"}
              </span>
            </p>
          </div>
          <p className="mt-2 text-xs text-zinc-500">
            RCPA baseline: {formatDate(selected.rcpaFirstMonth)} to {formatDate(selected.rcpaLastMonth)}
          </p>
          {detail.isLoading ? <LoadingState label="Loading doctor detail" compact /> : null}
          {detail.isError ? (
            <div className="mt-5 grid gap-4 text-sm">
              <WarningRegistration
                record={{
                  id: `doctor-detail-load-${selected.countryCode}-${selected.pcodeNormalized}`,
                  title: "Doctor drilldown load notes",
                  tone: "warning",
                  items: ["Doctor drilldown could not load full history. Backend detail views may need migration or refresh."],
                }}
              />
              <div className="rounded-md border border-zinc-800 bg-zinc-950 p-3 text-zinc-300">
                <p className="font-semibold">Doctor drilldown could not load full history.</p>
                <p className="mt-1 text-xs leading-5">
                  Showing the selected table row below. This usually means the backend detail endpoint
                  or one of the new sponsorship/RCPA views is not migrated or refreshed yet.
                </p>
              </div>
              <DoctorRowFallback selected={selected} />
            </div>
          ) : null}
          {detail.data ? (
            <div className="mt-5 grid min-w-0 gap-4 text-sm">
              <DoctorOutcomeEvidence detail={detail.data} />
              <section>
                <h3 className="font-semibold">Engagement history</h3>
                {detail.data.engagementHistory.length ? detail.data.engagementHistory.map((item, index) => (
                  <p key={`${item.requestId}-${index}`} className="mt-2 break-words rounded-md border border-zinc-800 bg-zinc-900 p-2">
                    {item.month}: {item.interventionName ?? "Activity"}
                  </p>
                )) : <p className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-2 text-zinc-500">No actual engagement rows for this doctor.</p>}
              </section>
              <section>
                <h3 className="font-semibold">Prescription trend</h3>
                {detail.data.prescriptionTrend.length ? detail.data.prescriptionTrend.map((item) => (
                  <p key={item.month} className="mt-2 break-words rounded-md border border-zinc-800 bg-zinc-900 p-2">
                    {item.month}: Cipla {item.ciplaPrescriptionQty.toLocaleString()} / Total {item.totalPrescriptionQty.toLocaleString()}
                  </p>
                )) : <p className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-2 text-zinc-500">No RCPA trend rows available.</p>}
              </section>
              <section>
                <h3 className="font-semibold">Brand mix</h3>
                {detail.data.brandMix.length ? detail.data.brandMix.map((item, index) => (
                  <p key={`${item.brandGroup}-${item.ownOrCompetitor}-${index}`} className="mt-2 break-words rounded-md border border-zinc-800 bg-zinc-900 p-2">
                    {item.brandGroup} ({item.ownOrCompetitor}): {item.prescriptionQty.toLocaleString()} qty / {item.prescriptionValueLocal.toLocaleString()} local value
                  </p>
                )) : <p className="mt-2 rounded-md border border-zinc-800 bg-zinc-900 p-2 text-zinc-500">No brand mix rows available for this doctor.</p>}
              </section>
            </div>
          ) : null}
        </> : null}
      </SidePanel>
    </main>
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
    <div className="grid w-full min-w-0 gap-1 text-sm">
      <span className="font-medium text-zinc-300">{label}</span>
      <SmoothSelect ariaLabel={label} value={value} options={options} placeholder={empty} onChange={onChange} />
    </div>
  );
}

function formatRoiOptions(options: Array<{ value: string; label: string }>) {
  return options.map((option) => ({ ...option, label: formatRoiSegment(option.value) }));
}

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString();
}

function formatSegment(value: string | null | undefined) {
  return formatRoiSegment(value);
}

function DoctorRowFallback({ selected }: { selected: DoctorRoiRow }) {
  return (
    <section className="grid gap-3">
      {selected.sponsorshipEngagementAmountMissingCount > 0 ? (
        <WarningRegistration
          record={{
            id: `doctor-fallback-amount-${selected.countryCode}-${selected.pcodeNormalized}`,
            title: "Doctor fallback evidence notes",
            tone: "warning",
            items: ["Prior sponsorship or engagement evidence exists, but at least one amount is unavailable."],
          }}
        />
      ) : null}
      <h3 className="font-semibold">Selected row evidence</h3>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <FallbackMetric label="Spend" value={`$${selected.totalRoiSpendUsd.toLocaleString()}`} />
        <FallbackMetric label="Cipla Rx" value={selected.ciplaPrescriptionQty.toLocaleString()} />
        <FallbackMetric label="Engagements" value={selected.engagementCount.toLocaleString()} />
        <FallbackMetric label="Sponsorships" value={selected.sponsorshipCount.toLocaleString()} />
        <FallbackMetric label="Paid engagements" value={selected.paidEngagementCount.toLocaleString()} />
        <FallbackMetric label="No-fee" value={selected.noFeeEngagementCount.toLocaleString()} />
      </div>
    </section>
  );
}

function FallbackMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-2">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 break-words font-semibold text-zinc-100">{value}</p>
    </div>
  );
}
