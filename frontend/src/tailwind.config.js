export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'sans-serif'] },
      colors: {
        bg: '#0f1117',
        surface: '#161b27',
        card: '#1a2235',
        card2: '#1e2a40',
        border: '#2a3a55',
        'hr-accent': '#22c55e',
        'hr-muted': '#16a34a',
        'ap-accent': '#38bdf8',
        'ap-muted': '#0284c7',
        warn: '#f59e0b',
        danger: '#ef4444',
        success: '#22c55e',
        muted: '#64748b',
        subtle: '#1e2d44',
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '20px',
      }
    },
  },
  plugins: [],
}