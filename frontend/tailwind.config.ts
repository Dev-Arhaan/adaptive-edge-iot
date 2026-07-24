import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#14180F",
        panel: "#1E2419",
        "panel-border": "#333B2C",
        bone: "#E8E6DE",
        muted: "#8B9184",
        "risk-low": "#6E9B7B",
        "risk-medium": "#D9A441",
        "risk-high": "#E4572E",
        "risk-emergency": "#C6362B",
        signal: "#8FBF6E",
      },
      fontFamily: {
        display: ["var(--font-space-grotesk)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
        data: ["var(--font-plex-mono)", "monospace"],
      },
    },
  },
};

export default config;