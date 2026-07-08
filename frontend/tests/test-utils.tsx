import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";

import { WarningCenterDock, WarningCenterProvider } from "../src/components/common/WarningCenter";

export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
}

export function renderWithProviders(ui: ReactElement) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <WarningCenterProvider>
        {ui}
        <WarningCenterDock />
      </WarningCenterProvider>
    </QueryClientProvider>,
  );
}
