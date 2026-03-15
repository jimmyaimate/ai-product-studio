import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0d0d0d",
        surface: "#1a1a1f",
        "surface-raised": "#22222a",
        border: "#2a2a35",
        accent: "#00e5a0",
        purple: "#a855f7",
        "text-primary": "#ffffff",
        "text-secondary": "#9ca3af",
        "text-muted": "#4b5563",
        "tag-bg": "#1e2d28",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backgroundImage: {
        "accent-gradient": "linear-gradient(135deg, #00e5a0 0%, #a855f7 100%)",
        "card-glow": "radial-gradient(ellipse at top left, rgba(0,229,160,0.06) 0%, transparent 60%)",
      },
      boxShadow: {
        "accent-sm": "0 0 12px rgba(0,229,160,0.15)",
        "accent-md": "0 0 24px rgba(0,229,160,0.2)",
        "card": "0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
      },
      keyframes: {
        fadeIn: { from: { opacity: "0" }, to: { opacity: "1" } },
        slideUp: { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};

export default config;
