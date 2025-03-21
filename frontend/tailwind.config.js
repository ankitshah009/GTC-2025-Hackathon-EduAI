/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f2eeff',
          100: '#e4ddff',
          200: '#c9baff',
          300: '#ad97ff',
          400: '#9274ff',
          500: '#7652ff',
          600: '#5e35b1', // Base primary color
          700: '#4527a0',
          800: '#301d80',
          900: '#1c1260',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}