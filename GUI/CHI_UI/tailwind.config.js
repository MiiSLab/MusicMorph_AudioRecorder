/** @type {import('tailwindcss').Config} */
export default {
	content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
	theme: {
		extend: {},
	},
	daisyui: {
		themes: [
			{
				dark: {
					'base-100': '#1F2023', // 將背景色設為透明
					'base-200': '#1F2023', // 次層背景色設為透明
					'base-300': '#1F2023', // 更深層背景色設為透明
				},
			},
		],
	},
	plugins: [require('tailwind-scrollbar'), require('daisyui')],
};
