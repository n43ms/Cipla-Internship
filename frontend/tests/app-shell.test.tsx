import { fireEvent, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

describe("App shell", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the execution governance shell", () => {
    renderWithProviders(<App />);

    expect(screen.getByRole("button", { name: /enter dashboard|click to continue/i })).toBeInTheDocument();
    expect(screen.getByText("Cipla EMEU/PBP analytics")).toBeInTheDocument();
    expect(screen.getByText(/Doctor ROI and Execution Intelligence/)).toBeInTheDocument();
    expect(screen.getByText("ExecAI")).toBeInTheDocument();
    expect(screen.getByText(/50\+ regional investment decisions/)).toBeInTheDocument();
  });

  it("exposes the business-user upload entry point after entering the app", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(dataQuality()), { status: 200 }),
    );

    renderWithProviders(<App />);
    fireEvent.click(screen.getByRole("button", { name: /enter dashboard|click to continue/i }));

    await waitFor(() => expect(screen.getByRole("button", { name: /upload new data files/i })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /upload new data files/i }));

    expect(screen.getByRole("heading", { name: "Upload new data/files" })).toBeInTheDocument();
    expect(screen.getByText("Choose Excel files")).toBeInTheDocument();
  });
});

function dataQuality() {
  return {
    meta: {
      generatedAt: "2026-06-19T00:00:00Z",
      latestIngestionStatus: "completed",
      filtersApplied: {},
      dataQualityFlags: [],
      limitations: [],
      sourceDerivationNotes: [],
    },
    latestIngestion: {
      id: "run-1",
      status: "completed",
      startedAt: null,
      completedAt: null,
      sourceFileCount: 1,
      totalRowsSeen: 1,
      totalRowsLoaded: 1,
      totalRowsSkipped: 0,
      warningCount: 0,
      errorCount: 0,
    },
  };
}
