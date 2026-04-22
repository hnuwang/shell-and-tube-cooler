import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
export default defineConfig(function () {
    var _a;
    var backendTarget = (_a = process.env.VITE_API_PROXY_TARGET) !== null && _a !== void 0 ? _a : "http://127.0.0.1:8010";
    return {
        plugins: [react()],
        resolve: {
            alias: {
                "@": path.resolve(__dirname, "./src"),
            },
        },
        server: {
            port: 5173,
            proxy: {
                "/api": {
                    target: backendTarget,
                    changeOrigin: true,
                },
            },
        },
    };
});
