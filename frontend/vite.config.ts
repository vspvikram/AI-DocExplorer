import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    build: {
        outDir: "../backend/static",
        emptyOutDir: true,
        sourcemap: true
    },
    server: {
        proxy: {
            "/ask": "http://127.0.0.1:5000",
            "/chat": "http://127.0.0.1:5000",
            "/version": "http://127.0.0.1:5000",
            "/login": "http://127.0.0.1:5000",
            "/authorize": "http://127.0.0.1:5000",
            "/clear_history": "http://127.0.0.1:5000",
            // proxy for the /content/<path> route
            "/content/*": {
                target: "http://127.0.0.1:5000/content",
                rewrite: (path) => path
            }
        }
    }
});

