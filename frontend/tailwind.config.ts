import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        accent: "#6aaea5",
        ink: "#e3e1dc",
        muted: "#969a9d",
        surface: "#0d0f10",
      },
      boxShadow: {
        panel: "0 18px 44px rgba(0, 0, 0, 0.24)",
        glow: "0 0 0 1px rgba(45, 212, 191, 0.12), 0 12px 30px rgba(0, 0, 0, 0.28)",
      },
      keyframes: {
        "page-enter": {
          "0%": { opacity: "0", transform: "translateY(5px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "drawer-enter": {
          "0%": { opacity: "0", transform: "translateX(18px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
      },
      animation: {
        "page-enter": "page-enter 440ms cubic-bezier(0.22, 1, 0.36, 1) both",
        "drawer-enter": "drawer-enter 380ms cubic-bezier(0.22, 1, 0.36, 1) both",
      },
    },
  },
  plugins: [],
} satisfies Config;
