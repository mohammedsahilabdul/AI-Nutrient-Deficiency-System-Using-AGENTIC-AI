/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
      colors: {
        surface: {
          DEFAULT: "rgb(12 14 22 / <alpha-value>)",
          elevated: "rgb(18 21 32 / <alpha-value>)",
          muted: "rgb(26 30 46 / <alpha-value>)",
        },
        accent: {
          cyan: "#22d3ee",
          blue: "#3b82f6",
          violet: "#8b5cf6",
        },
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(56, 189, 248, 0.35)",
        "glow-violet": "0 0 40px -10px rgba(139, 92, 246, 0.3)",
        card: "0 4px 24px -4px rgba(0, 0, 0, 0.45)",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out forwards",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
