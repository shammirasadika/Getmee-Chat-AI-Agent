import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
const printUrls = () => ({
  name: "print-urls",
  configureServer(server: any) {
    server.httpServer?.once("listening", () => {
      const addr = server.httpServer.address();
      const port = typeof addr === "object" ? addr.port : 8080;
      setTimeout(() => {
        console.log(`\n  \x1b[36m✔ GetMee Chat UI:\x1b[0m  http://localhost:${port}/`);
        console.log(`  \x1b[36m✔ Backend API:\x1b[0m    http://localhost:8080/`);
        console.log(`  \x1b[36m✔ Swagger Docs:\x1b[0m   http://localhost:8080/docs\n`);
      }, 100);
    });
  },
});

export default defineConfig(() => ({
  server: {
    host: "::",
    port: 5173,
    hmr: {
      overlay: false,
    },
    proxy: {
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
  preview: {
    host: "0.0.0.0",
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
  plugins: [react(), printUrls()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
