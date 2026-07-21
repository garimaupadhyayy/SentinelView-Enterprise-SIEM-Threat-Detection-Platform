/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Base surfaces -- deep blue-black, not pure black, so panels can
        // separate from the page without relying on borders alone.
        base: {
          950: "#080B0F",
          900: "#0D1319",
          800: "#121A22",
          700: "#1A2530",
          600: "#243241",
        },
        line: "#22303D",
        ink: {
          DEFAULT: "#E7EDF3",
          muted: "#8CA0B3",
          faint: "#5B6E80",
        },
        // Signal accent -- used sparingly for primary actions / "live" state.
        signal: {
          DEFAULT: "#2DD4BF",
          dim: "#1B7A70",
          glow: "#5EEAD4",
        },
        // Severity scale used consistently across alerts, badges, charts.
        sev: {
          info: "#5B8DEF",
          low: "#3FB6C7",
          medium: "#E5B93E",
          high: "#F2924A",
          critical: "#EF5A5A",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        sans: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(45,212,191,0.25), 0 0 24px -4px rgba(45,212,191,0.35)",
      },
      backgroundImage: {
        scan: "linear-gradient(180deg, rgba(45,212,191,0.06) 0%, rgba(45,212,191,0) 100%)",
      },
    },
  },
  plugins: [],
};
