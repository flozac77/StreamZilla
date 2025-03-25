/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'twitch': {
          'purple': '#9146FF',
          'dark': '#0E0E10',
          'light': '#18181B',
          'text': '#EFEFF1'
        }
      },
      animation: {
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-50vh)' },
        }
      }
    },
  },
  plugins: [],
} 