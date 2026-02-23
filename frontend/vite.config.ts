import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// VITE_PROXY_TARGET — where vite forwards /api, /static, /health requests.
// Docker: http://backend:8000 (container DNS, set via build arg)
// Local dev outside Docker: http://localhost:8000
const PROXY_TARGET = process.env.VITE_PROXY_TARGET ?? "http://localhost:8000";

const proxyRoutes = {
    "/api": { target: PROXY_TARGET, changeOrigin: true },
    "/static": { target: PROXY_TARGET, changeOrigin: true },
    "/health": { target: PROXY_TARGET, changeOrigin: true },
};

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        host: true,
        proxy: proxyRoutes,
    },
    preview: {
        port: 4173,
        host: true,
        proxy: proxyRoutes,
    },
    build: {
        outDir: "dist",
        sourcemap: false,
    },
});
