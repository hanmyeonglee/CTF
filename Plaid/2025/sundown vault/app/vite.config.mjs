import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [react()],
	css: {
		modules: {
			localsConvention: "camelCaseOnly",
		},
	},
	resolve: {
		alias: {
			"@": "/src",
		},
	},
	define: {
		__DEV__: false,
	},
	build: {
		outDir: "dist-ui",
	},
	server: {
		port: 3001,
		proxy: {
			"/api": {
				target: "http://127.0.0.1:80",
				changeOrigin: true,
				secure: false,
				ws: true,
			},
		},
	},
});
