import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { DataFreshnessBanner, EmptyState, ErrorState, LoadingState } from "../src/components/common/DataStateComponents";
import { renderWithProviders } from "./test-utils";

describe("Data state components", () => {
  it("renders freshness warnings and limitations visibly", () => {
    renderWithProviders(
      <DataFreshnessBanner
        meta={{
          generatedAt: "2026-06-19T00:00:00Z",
          latestIngestionStatus: "completed_with_warnings",
          filtersApplied: {},
          dataQualityFlags: ["weak_match_coverage", "provisional_fx", "no_rcpa"],
          limitations: ["Some rows use provisional FX.", "RCPA is historical baseline only."],
          sourceDerivationNotes: [],
        }}
      />,
    );

    expect(screen.getByText(/Latest ingestion status:/)).toBeInTheDocument();
    expect(screen.getByText("weak match coverage")).toBeInTheDocument();
    expect(screen.getByText("provisional fx")).toBeInTheDocument();
    expect(screen.getByText("no rcpa")).toBeInTheDocument();
    expect(screen.getByText("Some rows use provisional FX.")).toBeInTheDocument();
  });

  it("renders loading, empty, and error states with accessible labels", () => {
    renderWithProviders(
      <>
        <LoadingState label="Loading data quality" compact />
        <EmptyState title="No rows" detail="Nothing matched the current filters." />
        <ErrorState title="Data quality unavailable" />
      </>,
    );

    expect(screen.getByRole("status")).toHaveTextContent("Loading data quality");
    expect(screen.getByText("No rows")).toBeInTheDocument();
    expect(screen.getByText("Data quality unavailable")).toBeInTheDocument();
  });
});
