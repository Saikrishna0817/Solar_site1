/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        solar: {
          gold: '#F5A623',
          orange: '#E8590C',
          amber: '#D97706',
        },
        tech: {
          cyan: '#06B6D4',
          teal: '#14B8A6',
          blue: '#3B82F6',
        },
        space: {
          deep: '#0A0E1A',
          panel: '#0D1B2A',
          surface: '#111B2E',
          border: '#1E3A52',
          light: '#1B2D45',
        },
        txt: {
          primary: '#E8F4FD',
          secondary: '#8BA8BF',
          dim: '#5A7A94',
        },
        success: '#10B981',
        warning: '#8B5CF6',
      },
      fontSize: {
        '2xs': ['0.65rem', { lineHeight: '1rem' }],
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-solar': 'linear-gradient(135deg, #F5A623 0%, #E8590C 100%)',
        'gradient-tech': 'linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)',
        'gradient-hero': 'radial-gradient(ellipse at 30% 50%, rgba(245,166,35,0.08) 0%, transparent 50%), radial-gradient(ellipse at 70% 20%, rgba(6,182,212,0.06) 0%, transparent 50%)',
      },
      boxShadow: {
        'glow-gold': '0 0 20px rgba(245,166,35,0.3)',
        'glow-cyan': '0 0 20px rgba(6,182,212,0.3)',
        'glow-lg': '0 0 40px rgba(245,166,35,0.2)',
        'glass': '0 8px 32px rgba(0,0,0,0.3)',
        'card-hover': '0 12px 40px rgba(245,166,35,0.1), 0 0 0 1px rgba(245,166,35,0.05)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 20s linear infinite',
        'gradient': 'gradient 8s ease infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float-up': 'float-up 0.6s cubic-bezier(0.22, 1, 0.36, 1) both',
        'entrance': 'entrance-scale 0.5s cubic-bezier(0.22, 1, 0.36, 1) both',
        'fade-blur': 'fade-in-blur 0.7s ease-out both',
        'breathe': 'card-breathe 4s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(245,166,35,0.3)' },
          '100%': { boxShadow: '0 0 25px rgba(245,166,35,0.6)' },
        },
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
    },
  },
  plugins: [],
}
