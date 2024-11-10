/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './*.html'],
  darkMode: ['media', 'class'],
  mode: 'jit',
  theme: {
  	extend: {
  		fontFamily: {
  			inter: ['Inter', 'sans-serif']
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {}
  	}
  },
    plugins: [require("tailwindcss-animate")]
};
