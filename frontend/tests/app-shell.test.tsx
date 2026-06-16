import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

describe("App shell", () => {
  it("renders the platform name", () => {
    renderWithProviders(<App />);

    expect(screen.getByText("Execution Intelligence Platform")).toBeInTheDocument();
  });
});
