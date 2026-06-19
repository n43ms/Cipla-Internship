import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getDoctorDetail, getDoctorRoi } from "../api/doctors";
import { getFilters } from "../api/filters";
import { DataFreshnessBanner, EmptyState, ErrorState } from "../components/common/DataStateComponents";
import { DoctorRoiCards, DoctorRoiTable, DoctorScatter, QuadrantMatrix } from "../components/doctors/DoctorRoiComponents";
import type { DoctorRoiRow } from "../types/api";

export function DoctorRoi() {
  const [selected, setSelected] = useState<DoctorRoiRow | null>(null);
  const [country, setCountry] = useState("");
  const [monthStart, setMonthStart] = useState("");
  const [monthEnd, setMonthEnd] = useState("");
  const [brand, setBrand] = useState("");
  const [speciality, setSpeciality] = useState("");
  const [doctorClass, setDoctorClass] = useState("");
  const [roiSegment, setRoiSegment] = useState("");
  const [includeOutOfScope, setIncludeOutOfScope] = useState(false);
  const [page, setPage] = useState(1);

  const filters = useQuery({ queryKey: ["filters"], queryFn: getFilters });
  const roi = useQuery({
    queryKey: ["doctor-roi", country, monthStart, monthEnd, brand, speciality, doctorClass, roiSegment, includeOutOfScope, page],
    queryFn: () => getDoctorRoi({ country, monthStart, monthEnd, brand, speciality, doctorClass, roiSegment, includeOutOfScope, page, pageSize: 50 }),
  });
  const detail = useQuery({
    queryKey: ["doctor-detail", selected?.countryCode, selected?.pcodeNormalized],
    queryFn: () => getDoctorDetail(selected!.countryCode, selected!.pcodeNormalized),
    enabled: Boolean(selected),
  });

  if (roi.isLoading) return <main className="p-6 text-sm text-slate-500">Loading doctor ROI</main>;
  if (roi.isError) return <main className="p-6"><ErrorState title="Doctor ROI unavailable" /></main>;
  if (!roi.data) return null;

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">Doctor ROI</p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-950">Doctor opportunities and missed value</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Connects actual attended doctors to allocated spend and RCPA prescription behavior using country-scoped Pcodes.
          </p>
        </header>
        <DataFreshnessBanner meta={roi.data.meta} />
        <section className="dashboard-card p-4">
          <div className="grid gap-3 md:grid-cols-4">
            <Select label="Country" value={country} options={filters.data?.countries ?? []} empty="All countries" onChange={(value) => { setCountry(value); setPage(1); }} />
            <Select label="Start month" value={monthStart} options={filters.data?.months ?? []} empty="Any start" onChange={(value) => { setMonthStart(value); setPage(1); }} />
            <Select label="End month" value={monthEnd} options={filters.data?.months ?? []} empty="Any end" onChange={(value) => { setMonthEnd(value); setPage(1); }} />
            <Select label="Brand baseline" value={brand} options={filters.data?.brands ?? []} empty="All brands" onChange={(value) => { setBrand(value); setPage(1); }} />
            <Select label="Speciality" value={speciality} options={filters.data?.specialities ?? []} empty="All specialities" onChange={(value) => { setSpeciality(value); setPage(1); }} />
            <Select label="Doctor class" value={doctorClass} options={filters.data?.doctorClasses ?? []} empty="All classes" onChange={(value) => { setDoctorClass(value); setPage(1); }} />
            <Select label="ROI segment" value={roiSegment} options={filters.data?.roiSegments ?? []} empty="All segments" onChange={(value) => { setRoiSegment(value); setPage(1); }} />
            <label className="flex items-center gap-2 self-end rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
              <input type="checkbox" checked={includeOutOfScope} onChange={(event) => { setIncludeOutOfScope(event.target.checked); setPage(1); }} />
              Include all loaded markets
            </label>
            <button className="soft-button self-end rounded-md border border-slate-200 px-4 py-2 text-sm" onClick={() => { setCountry(""); setMonthStart(""); setMonthEnd(""); setBrand(""); setSpeciality(""); setDoctorClass(""); setRoiSegment(""); setIncludeOutOfScope(false); setPage(1); }}>Clear</button>
          </div>
        </section>
        <div className="dashboard-card border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
          Doctor ROI defaults to Nepal and Sri Lanka primary markets. RCPA prescription data is a historical baseline. Brand filters identify doctors with that brand in baseline RCPA; displayed ROI metrics remain all-brand doctor totals.
        </div>
        <DoctorRoiCards data={roi.data} />
        {roi.data.rows.length ? (
          <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(22rem,0.6fr)]">
            <DoctorScatter rows={roi.data.rows} />
            <QuadrantMatrix counts={roi.data.quadrantCounts} />
            <div className="xl:col-span-2">
              <DoctorRoiTable rows={roi.data.rows} page={page} pageSize={roi.data.pageSize} total={roi.data.total} onPageChange={setPage} onSelect={setSelected} />
            </div>
          </div>
        ) : (
          <EmptyState title="No doctor ROI rows" detail="Doctor ROI needs actual attendance Pcodes or RCPA summary rows." />
        )}
      </div>
      {selected ? (
        <aside className="fixed inset-y-0 right-0 z-20 w-full max-w-lg overflow-y-auto border-l border-slate-200 bg-white p-5 shadow-2xl transition">
          <button className="soft-button rounded-md border border-slate-200 px-3 py-1 text-sm" onClick={() => setSelected(null)}>Close</button>
          <h2 className="mt-4 text-xl font-semibold">{selected.doctorName ?? selected.pcodeNormalized}</h2>
          <p className="text-sm text-slate-500">{selected.countryCode} - {selected.roiSegment.replaceAll("_", " ")}</p>
          <p className="mt-2 text-xs text-slate-500">
            RCPA baseline: {formatDate(selected.rcpaFirstMonth)} to {formatDate(selected.rcpaLastMonth)}
          </p>
          {detail.isLoading ? <p className="mt-4 text-sm text-slate-500">Loading detail</p> : null}
          {detail.data ? (
            <div className="mt-5 grid gap-4 text-sm">
              <section>
                <h3 className="font-semibold">Engagement history</h3>
                {detail.data.engagementHistory.length ? detail.data.engagementHistory.map((item, index) => (
                  <p key={`${item.requestId}-${index}`} className="mt-2 rounded-md bg-slate-50 p-2">
                    {item.month}: {item.interventionName ?? "Activity"} - {item.fxRateStatus ?? "fx unknown"}
                  </p>
                )) : <p className="mt-2 rounded-md bg-slate-50 p-2 text-slate-500">No actual engagement rows for this doctor.</p>}
              </section>
              <section>
                <h3 className="font-semibold">Prescription trend</h3>
                {detail.data.prescriptionTrend.length ? detail.data.prescriptionTrend.map((item) => (
                  <p key={item.month} className="mt-2 rounded-md bg-slate-50 p-2">
                    {item.month}: Cipla {item.ciplaPrescriptionQty.toLocaleString()} / Total {item.totalPrescriptionQty.toLocaleString()}
                  </p>
                )) : <p className="mt-2 rounded-md bg-slate-50 p-2 text-slate-500">No RCPA trend rows available.</p>}
              </section>
              <section>
                <h3 className="font-semibold">Brand mix</h3>
                {detail.data.brandMix.length ? detail.data.brandMix.map((item) => (
                  <p key={`${item.brandGroup}-${item.ownOrCompetitor}`} className="mt-2 rounded-md bg-slate-50 p-2">
                    {item.brandGroup} ({item.ownOrCompetitor}): {item.prescriptionQty.toLocaleString()} qty / {item.prescriptionValueLocal.toLocaleString()} local value
                  </p>
                )) : <p className="mt-2 rounded-md bg-slate-50 p-2 text-slate-500">No brand mix rows available for this doctor.</p>}
              </section>
            </div>
          ) : null}
        </aside>
      ) : null}
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
    <label className="grid gap-1 text-sm">
      <span className="font-medium text-slate-700">{label}</span>
      <select className="rounded-md border border-slate-300 bg-white px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">{empty}</option>
        {options.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
      </select>
    </label>
  );
}

function formatDate(value: string | null) {
  if (!value) return "not available";
  return new Date(value).toLocaleDateString();
}
