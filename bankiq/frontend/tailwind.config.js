/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        bank: {
          navy: "#0B1F3A",
          gold: "#C9A227",
          slate: "#64748B",
        },
      },
    },
  },
  plugins: [],
};
