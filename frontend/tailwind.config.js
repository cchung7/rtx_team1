/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        aqi: {
          good: "#00E400",
          moderate: "#FFFF00",
          ufs: "#FF7E00",
          unhealthy: "#FF0000",
          veryunhealthy: "#8F3F97",
          hazardous: "#7E0023",
        },
        brand: {
          primary: "#2563eb",
          secondary: "#64748b",
        }
      },
      boxShadow: {
        card: "0 10px 25px rgba(0,0,0,0.06)",
      },
      borderRadius: {
        xl2: "1rem",
      }
    },
  },
  plugins: [],
}
