/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#07090f',
        surface: '#0d1117',
        card: '#111827',
        card2: '#161f32',
        border: '#1f2d45',
        'hr-accent': '#22c55e',
        'ap-accent': '#38bdf8',
        warn: '#f59e0b',
        danger: '#ef4444',
        muted: '#64748b',
      }
    },
  },
  plugins: [],
}