import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { getDoctorDetail, getDoctorRoi } from "../api/doctors";
import { DataFreshnessBanner, EmptyState, ErrorState } from "../components/common/DataStateComponents";
import { DoctorRoiCards, DoctorRoiTable, DoctorScatter, QuadrantMatrix } from "../components/doctors/DoctorRoiComponents";
import type { DoctorRoiRow } from "../types/api";

export function DoctorRoi() {
  const [selected, setSelected] = useState<DoctorRoiRow | null>(null);
  const roi = useQuery({ queryKey: ["doctor-roi"], queryFn: () => getDoctorRoi({ pageSize: 50 }) });
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
        <DoctorRoiCards data={roi.data} />
        {roi.data.rows.length ? (
          <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(22rem,0.6fr)]">
            <DoctorScatter rows={roi.data.rows} />
            <QuadrantMatrix counts={roi.data.quadrantCounts} />
            <div className="xl:col-span-2">
              <DoctorRoiTable rows={roi.data.rows} onSelect={setSelected} />
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
          <p className="text-sm text-slate-500">{selected.countryCode} · {selected.roiSegment.replaceAll("_", " ")}</p>
          {detail.isLoading ? <p className="mt-4 text-sm text-slate-500">Loading detail</p> : null}
          {detail.data ? (
            <div className="mt-5 grid gap-4 text-sm">
              <section>
                <h3 className="font-semibold">Engagement history</h3>
                {detail.data.engagementHistory.map((item, index) => (
                  <p key={`${item.requestId}-${index}`} className="mt-2 rounded-md bg-slate-50 p-2">
                    {item.month}: {item.interventionName ?? "Activity"} · {item.fxRateStatus ?? "fx unknown"}
                  </p>
                ))}
              </section>
              <section>
                <h3 className="font-semibold">Prescription trend</h3>
                {detail.data.prescriptionTrend.map((item) => (
                  <p key={item.month} className="mt-2 rounded-md bg-slate-50 p-2">
                    {item.month}: Cipla {item.ciplaPrescriptionQty.toLocaleString()} / Total {item.totalPrescriptionQty.toLocaleString()}
                  </p>
                ))}
              </section>
            </div>
          ) : null}
        </aside>
      ) : null}
    </main>
  );
}
