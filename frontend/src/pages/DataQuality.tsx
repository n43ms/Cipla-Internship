import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { getDataQuality } from "../api/filters";
import { DataFreshnessBanner, EmptyState, ErrorState, KpiCard, LoadingState } from "../components/common/DataStateComponents";
import { SortableHeader, useSortableRows, type SortValue } from "../components/common/SortableTable";
import type { DataQualityResponse } from "../types/api";

type ValidationIssue = DataQualityResponse["validationIssues"][number];

const VALIDATION_SORT_ACCESSORS = {
  severity: (row: ValidationIssue) => row.severity,
  file: (row: ValidationIssue) => row.sourceFile,
  code: (row: ValidationIssue) => row.errorCode,
  message: (row: ValidationIssue) => row.message,
};

export function DataQuality() {
  const quality = useQuery({ queryKey: ["data-quality"], queryFn: getDataQuality });

  if (quality.isLoading) return <main><LoadingState label="Loading data quality" /></main>;
  if (quality.isError) return <main className="p-6"><ErrorState title="Data quality unavailable" /></main>;
  if (!quality.data) return null;

  const data = quality.data;
  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Trust layer</p>
          <h1 className="page-title">Data quality</h1>
          <p className="page-copy">
            Shows freshness, row counts, validation issues, match coverage, Pcode coverage, RCPA coverage, FX quality, workflow coverage, and unmatched records before anyone acts on KPIs.
          </p>
        </header>
        <DataFreshnessBanner meta={data.meta} />
        <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Loaded files" value={`${data.loadedFileCount}/${data.sourceFileCount}`} detail={data.latestIngestion.status} />
          <KpiCard label="Rows loaded" value={data.rowsLoaded.toLocaleString()} detail={`${data.rowsSkipped.toLocaleString()} skipped`} />
          <KpiCard label="Match coverage" value={`${Math.round(data.matchCoverage * 100)}%`} detail={`${data.unmatchedEventCount} unmatched records`} />
          <KpiCard label="RCPA coverage" value={`${Math.round(data.rcpaCoverage * 100)}%`} detail={`${data.derivedSnapshotCount} derived snapshots`} />
          <KpiCard label="Pcode coverage" value={`${Math.round(data.pcodeCoverage * 100)}%`} />
          <KpiCard label="Missing FX" value={data.missingFxCount} detail={`${data.provisionalFxCount} provisional`} />
          <KpiCard label="BTU/BTC issues" value={data.btuBtcReconciliationIssueCount} />
          <KpiCard label="Workflow coverage" value={`${Math.round(data.requestWorkflowCoverage * 100)}%`} detail={`Post ${Math.round(data.postWorkflowCoverage * 100)}%`} />
          <KpiCard label="Missing actual Pcodes" value={data.actualAttendanceMissingPcodeCount} detail={`${data.unallocatedDoctorSpendUsd.toLocaleString()} USD unallocated`} />
          <KpiCard label="LKR FX seed" value={data.officialLkrRateToUsd ? "Official" : "Missing"} detail={data.staticFxSeedDate ?? "No seed date"} />
        </div>
        <div className="grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-2">
          <SimpleTable
            title="Source file participation"
            detail="Latest run per file. Current validation counts should be interpreted against this scope."
            headers={["File", "Type", "Status", "Loaded", "Skipped"]}
            rows={data.sourceFiles.map((row) => [
              row.sourceFile ?? "-",
              row.sourceType ?? "-",
              row.status ?? "-",
              row.rowsLoaded.toLocaleString(),
              row.rowsSkipped.toLocaleString(),
            ])}
          />
          <SimpleTable
            title="FX quality"
            detail="LKR must use the company rate. Missing-FX currencies stay local-only."
            headers={["Currency", "Status", "Rate", "Date", "Rows"]}
            rows={data.fxQuality.map((row) => [
              row.currencyCode,
              row.rateStatus,
              row.rateToUsd?.toString() ?? "-",
              row.rateDate ?? "-",
              row.rowCount.toLocaleString(),
            ])}
          />
          <SimpleTable
            title="Unmatched by source"
            detail="Primary-scope reconciliation gaps grouped by source and reason."
            headers={["Source", "Reason", "Records"]}
            rows={data.unmatchedBySource.map((row) => [row.sourceType, row.reasonCode.replaceAll("_", " "), row.recordCount.toLocaleString()])}
          />
          <SimpleTable
            title="Unmatched records"
            detail="Sample of records that need review before treating KPIs as final."
            headers={["Source", "Country", "Month", "Event", "Reason"]}
            rows={data.unmatchedRecords.map((row) => [
              row.sourceType,
              row.country,
              row.month,
              row.eventName ?? "-",
              (row.reasonCode ?? "unknown").replaceAll("_", " "),
            ])}
          />
        </div>
        <ValidationTable data={data} />
      </div>
    </main>
  );
}

function SimpleTable({ title, detail, headers, rows }: { title: string; detail: string; headers: string[]; rows: string[][] }) {
  const accessors = useMemo(
    () => Object.fromEntries(headers.map((_, index) => [String(index), (row: string[]) => row[index] as SortValue])) as Record<string, (row: string[]) => SortValue>,
    [headers],
  );
  const sorted = useSortableRows(rows, accessors);
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold">{title}</h2>
        <p className="text-sm text-zinc-500">{detail}</p>
      </div>
      {rows.length ? (
        <div className="table-scroll max-h-96 overflow-y-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="table-head sticky top-0">
              <tr>{headers.map((header, index) => <SortableHeader key={header} column={String(index)} label={header} sort={sorted.sort} onSort={sorted.onSort} />)}</tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {sorted.rows.map((row, index) => (
                <tr key={`${title}-${index}`}>
                  {row.map((cell, cellIndex) => <td key={`${title}-${index}-${cellIndex}`} className="max-w-[18rem] truncate px-4 py-3">{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState title={`No ${title.toLowerCase()}`} detail="No rows were returned by the backend." />
      )}
    </div>
  );
}

function ValidationTable({ data }: { data: DataQualityResponse }) {
  const sorted = useSortableRows(data.validationIssues, VALIDATION_SORT_ACCESSORS);
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold">Validation drilldown</h2>
        <p className="text-sm text-zinc-500">{data.validationErrorCount} errors and {data.validationWarningCount} warnings in recent ingestion history.</p>
      </div>
      {data.validationIssues.length ? (
        <div className="table-scroll">
          <table className="min-w-full text-left text-sm">
            <thead className="table-head">
              <tr>
                <SortableHeader column="severity" label="Severity" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="file" label="File" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="code" label="Code" sort={sorted.sort} onSort={sorted.onSort} />
                <SortableHeader column="message" label="Message" sort={sorted.sort} onSort={sorted.onSort} />
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {sorted.rows.map((issue, index) => (
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
  );
}
