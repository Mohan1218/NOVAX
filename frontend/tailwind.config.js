/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        novax: {
          bg: '#070b18',
          sidebar: '#080d1e',
          card: '#0c142b',
          cardHover: '#111b38',
          border: '#172344',
          borderLight: '#243564',
          primary: '#2b59ff',
          primaryHover: '#3b68ff',
          cyan: '#00d2ff',
          purple: '#8b5cf6',
          muted: '#8e9bb4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      },
      boxShadow: {
        'glow-sm': '0 0 15px rgba(59, 130, 246, 0.2)',
        'glow-md': '0 0 25px rgba(59, 130, 246, 0.3)',
        'glow-lg': '0 0 40px rgba(59, 130, 246, 0.4)',
        'glow-cyan': '0 0 25px rgba(6, 182, 212, 0.35)',
        'glow-purple': '0 0 25px rgba(139, 92, 246, 0.35)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        }
      }
    },
  },
  plugins: [],
}
