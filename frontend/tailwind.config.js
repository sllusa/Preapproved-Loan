/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f0ff',
          100: '#b3d4ff',
          200: '#80b8ff',
          300: '#4d9cff',
          400: '#1a80ff',
          500: '#0066CC',
          600: '#0052a3',
          700: '#004C99',
          800: '#003d7a',
          900: '#002e5c',
        },
      },
    },
  },
  plugins: [],
};
