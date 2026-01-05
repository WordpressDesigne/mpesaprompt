/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#4f46e5',
          600: '#4338ca',
        },
        secondary: {
          500: '#10b981',
        },
        neutral: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          400: '#94a3b8',
          600: '#475569',
          800: '#1e293b',
          900: '#0f172a',
        },
        error: {
          500: '#ef4444',
        },
        success: {
          500: '#22c55e',
        },
      },
    },
  },
  plugins: [],
}
