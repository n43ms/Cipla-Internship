import { useQuery } from "@tanstack/react-query";

import { getDataQuality } from "../api/filters";
import { DataFreshnessBanner, EmptyState, ErrorState, KpiCard } from "../components/common/DataStateComponents";

export function DataQuality() {
  const quality = useQuery({ queryKey: ["data-quality"], queryFn: getDataQuality });

  if (quality.isLoading) return <main className="p-6 text-sm text-slate-500">Loading data quality</main>;
  if (quality.isError) return <main className="p-6"><ErrorState title="Data quality unavailable" /></main>;
  if (!quality.data) return null;

  const data = quality.data;
  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="text-xs font-semibold uppercase tracking-wide text-cyan-700">Trust layer</p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-950">Data quality</h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Shows freshness, row counts, validation issues, match coverage, Pcode coverage, RCPA coverage, FX quality, workflow coverage, and unmatched records before anyone acts on KPIs.
          </p>
        </header>
        <DataFreshnessBanner meta={data.meta} />
        <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Loaded files" value={`${data.loadedFileCount}/${data.sourceFileCount}`} detail={data.latestIngestion.status} />
          <KpiCard label="Rows loaded" value={data.rowsLoaded.toLocaleString()} detail={`${data.rowsSkipped.toLocaleString()} skipped`} />
          <KpiCard label="Match coverage" value={`${Math.round(data.matchCoverage * 100)}%`} detail={`${data.unmatchedEventCount} unmatched records`} />
          <KpiCard label="RCPA coverage" value={`${Math.round(data.rcpaCoverage * 100)}%`} detail={`${data.derivedSnapshotCount} derived snapshots`} />
          <KpiCard label="Pcode coverage" value={`${Math.round(data.pcodeCoverage * 100)}%`} />
          <KpiCard label="Missing FX" value={data.missingFxCount} detail={`${data.provisionalFxCount} provisional`} />
          <KpiCard label="BTU/BTC issues" value={data.btuBtcReconciliationIssueCount} />
          <KpiCard label="Workflow coverage" value={`${Math.round(data.requestWorkflowCoverage * 100)}%`} detail={`Post ${Math.round(data.postWorkflowCoverage * 100)}%`} />
        </div>
        <div className="dashboard-card overflow-hidden">
          <div className="border-b border-slate-200 p-4">
            <h2 className="font-semibold">Validation drilldown</h2>
            <p className="text-sm text-slate-500">{data.validationErrorCount} errors and {data.validationWarningCount} warnings in recent ingestion history.</p>
          </div>
          {data.validationIssues.length ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-4 py-3">Severity</th>
                    <th className="px-4 py-3">File</th>
                    <th className="px-4 py-3">Code</th>
                    <th className="px-4 py-3">Message</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.validationIssues.map((issue, index) => (
                    <tr key={`${issue.errorCode}-${index}`}>
                      <td className="px-4 py-3">{issue.severity}</td>
                      <td className="max-w-[18rem] truncate px-4 py-3">{issue.sourceFile ?? "-"}</td>
                      <td className="px-4 py-3">{issue.errorCode}</td>
                      <td className="px-4 py-3">{issue.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState title="No validation issues" detail="No recent validation issues were returned by the backend." />
          )}
        </div>
      </div>
    </main>
  );
}
