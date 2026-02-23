import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend URL used for dev-server API proxy and injected into the app bundle.
const BACKEND_URL = process.env.VITE_BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
    plugins: [react()],
    define: {
        // Available as import.meta.env.VITE_BACKEND_URL at runtime
    },
    server: {
        port: 5173,
        host: true,
        proxy: {
            "/api": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
            "/static": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
            "/health": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
        },
    },
    preview: {
        port: 4173,
        host: true,
        // Proxy also needed for the production-preview container
        proxy: {
            "/api": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
            "/static": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
            "/health": {
                target: BACKEND_URL,
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: "dist",
        sourcemap: false,
    },
});
