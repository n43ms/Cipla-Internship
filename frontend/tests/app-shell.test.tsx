import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../src/App";
import { renderWithProviders } from "./test-utils";

describe("App shell", () => {
  it("renders the execution governance shell", () => {
    renderWithProviders(<App />);

    expect(screen.getByRole("button", { name: /click to continue/i })).toBeInTheDocument();
    expect(screen.getByText("Execution intelligence platform")).toBeInTheDocument();
  });
});
