import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DoctorRoi } from "../src/pages/DoctorRoi";
import { renderWithProviders } from "./test-utils";

const ok = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

describe("Doctor ROI page", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders ROI cards, quadrant matrix, table, no-RCPA states, and detail drawer", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
      const url = String(input);
      if (url.includes("/api/filters")) return ok(filters());
      if (url.includes("/api/doctors/LK/1001")) return ok(doctorDetail());
      if (url.includes("/api/doctors/roi")) return ok(doctorRoi());
      return ok({});
    });

    renderWithProviders(<DoctorRoi />);

    await waitFor(() => expect(screen.getByText("Doctor opportunities and missed value")).toBeInTheDocument());
    expect(screen.getByText("Doctor ROI rows")).toBeInTheDocument();
    expect(screen.getByText("ROI quadrant matrix")).toBeInTheDocument();
    expect(screen.getByText("Dr Test")).toBeInTheDocument();
    expect(screen.getByText("No RCPA rows")).toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: "Open" })[0]);
    await waitFor(() => expect(screen.getByText("Engagement history")).toBeInTheDocument());
    expect(screen.getByText("Prescription trend")).toBeInTheDocument();
    expect(screen.getByText("Brand mix")).toBeInTheDocument();
  });
});

function filters() {
  return {
    countries: [{ value: "LK", label: "Sri Lanka" }],
    months: [{ value: "2026-05", label: "2026-05" }],
    interventionTypes: [],
    brands: [{ value: "Brand A", label: "Brand A" }],
    specialities: [{ value: "Cardiology", label: "Cardiology" }],
    doctorClasses: [{ value: "A", label: "A" }],
    roiSegments: [{ value: "high_value_unengaged", label: "high value unengaged" }],
    latestIngestionStatus: "completed_with_warnings",
  };
}

function meta() {
  return {
    generatedAt: "2026-06-19T00:00:00Z",
    latestIngestionStatus: "completed_with_warnings",
    filtersApplied: {},
    dataQualityFlags: ["no_rcpa"],
    limitations: ["Doctor ROI defaults to primary markets."],
    sourceDerivationNotes: [],
  };
}

function doctorRoi() {
  return {
    meta: meta(),
    page: 1,
    pageSize: 50,
    total: 2,
    sort: "ciplaPrescriptionQty",
    sortDirection: "desc",
    darkHorseCount: 1,
    noRcpaCount: 1,
    missingFxCount: 0,
    provisionalFxCount: 0,
    brandFilterMode: null,
    periodFilterMode: "engagement_period",
    quadrantCounts: { "low effort / high reward": 1, "insufficient data": 1 },
    segmentCounts: { high_value_unengaged: 1, no_rcpa: 1 },
    rows: [
      doctorRow({ doctorName: "Dr Test", pcodeNormalized: "1001", hasRcpa: true, roiSegment: "high_value_unengaged" }),
      doctorRow({ doctorName: "Dr Missing RCPA", pcodeNormalized: "2002", hasRcpa: false, roiSegment: "no_rcpa", quadrantLabel: "insufficient data" }),
    ],
  };
}

function doctorDetail() {
  return {
    meta: meta(),
    profile: doctorRow({ doctorName: "Dr Test", pcodeNormalized: "1001", hasRcpa: true, roiSegment: "high_value_unengaged" }),
    engagementHistory: [{ requestId: "REQ-1", interventionName: "Diabetes CME", interventionType: "CME", month: "2026-05", actualInterventionDate: "2026-05-10", totalRoiSpendUsd: 10, fxRateStatus: "official" }],
    prescriptionTrend: [{ month: "2026-05", ciplaPrescriptionQty: 100, competitorPrescriptionQty: 50, totalPrescriptionQty: 150 }],
    brandMix: [{ brandGroup: "Brand A", ownOrCompetitor: "own", prescriptionQty: 100, prescriptionValueLocal: 2500 }],
  };
}

function doctorRow(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    countryCode: "LK",
    countryName: "Sri Lanka",
    pcodeNormalized: "1001",
    doctorName: "Dr Test",
    speciality: "Cardiology",
    doctorClass: "A",
    activeStatus: "Active",
    engagementCount: 0,
    firstEngagementDate: null,
    lastEngagementDate: null,
    directHcpBtuSpendUsd: 0,
    overheadBtcSpendUsd: 0,
    totalRoiSpendUsd: 0,
    ciplaPrescriptionQty: 100,
    competitorPrescriptionQty: 50,
    totalPrescriptionQty: 150,
    ciplaShareQty: 0.66,
    spendPerCiplaPrescriptionUsd: null,
    roiSegment: "high_value_unengaged",
    quadrantX: 0,
    quadrantY: 100,
    quadrantLabel: "low effort / high reward",
    darkHorseFlag: true,
    darkHorseUnengagedFlag: true,
    highValueEngagedFlag: false,
    hasRcpa: true,
    hasMissingFx: false,
    hasProvisionalFx: false,
    rcpaFirstMonth: "2025-04-01",
    rcpaLastMonth: "2026-03-01",
    rcpaMonthCount: 12,
    ...overrides,
  };
}
