/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 20px 50px -20px rgba(15, 23, 42, 0.45)',
      },
      colors: {
        accent: {
          50: '#eef8ff',
          100: '#d9f2ff',
          500: '#38bdf8',
          600: '#0ea5e9',
        },
      },
    },
  },
  plugins: [],
}

