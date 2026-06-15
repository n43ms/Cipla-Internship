import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        accent: "#0f766e",
        ink: "#111827",
        muted: "#64748b",
        surface: "#f8fafc",
      },
    },
  },
  plugins: [],
} satisfies Config;
