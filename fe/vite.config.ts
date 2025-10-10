import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendPort = env.VITE_BACKEND_PORT || "8000";
  const apiBase = env.VITE_API_BASE || "/api";
  const wsPath = env.VITE_WS_URL || "/ws";

  console.log(`[OFC] Backend port: ${backendPort}`);
  console.log(`[OFC] API base: ${apiBase}`);
  console.log(`[OFC] WebSocket path: ${wsPath}`);

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: apiBase.startsWith("/") ? {
        [apiBase]: {
          target: `http://127.0.0.1:${backendPort}`,
          changeOrigin: true,
          rewrite: (p) => p.replace(/^\/api/, ""),
        },
        [wsPath]: {
          target: `ws://127.0.0.1:${backendPort}`,
          changeOrigin: true,
          ws: true,
        },
      } : undefined
    },
  };
});
