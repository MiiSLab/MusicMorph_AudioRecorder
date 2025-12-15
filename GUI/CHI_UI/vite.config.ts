import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
	base: './',
	plugins: [react()],
	server: {
    open: true, // 啟動開發伺服器時自動打開瀏覽器
    port: 3000, // 與 CRA 一樣的預設埠號
  },
	build: {
		target: 'node20',
		minify: false,
		sourcemap: true,
		outDir: './dist',
		rollupOptions: {
			output: {
				format: 'cjs',
				dir: path.resolve(__dirname, 'dist'),
				entryFileNames: 'assets/[name].js',
				chunkFileNames: 'assets/[name].js',
				assetFileNames: 'assets/[name].[ext]',
			},
			external: ['sharp'],
		},
	},
	optimizeDeps: {
		include: ['sharp'],
	},
});
