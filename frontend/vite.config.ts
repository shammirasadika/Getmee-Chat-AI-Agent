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
        console.log(`  \x1b[36m✔ Backend API:\x1b[0m    http://localhost:8001/`);
        console.log(`  \x1b[36m✔ Swagger Docs:\x1b[0m   http://localhost:8001/docs\n`);
      }, 100);
    });
  },
});

export default defineConfig(() => ({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
    proxy: {
      "/api": {
        target: "http://localhost:8001",
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
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
        widget: path.resolve(__dirname, "widget/widget.ts"),
      },
      output: [
        {
          // Main app bundle
          entryFileNames: "[name].js",
          chunkFileNames: "chunks/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash][extname]",
          dir: "dist/app",
        },
        {
          // Widget bundle (separate)
          entryFileNames: "[name].js",
          chunkFileNames: "chunks/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash][extname]",
          dir: "dist/widget",
        },
      ],
    },
    minify: "terser",
  },
}));
