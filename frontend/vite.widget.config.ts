import { defineConfig } from "vite";
import path from "path";

// Widget loader is pure vanilla JS/TS — no React needed
export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, "widget/widget.ts"),
      name: "GetMeeChat",
      fileName: () => "getmee-chatbot.js",
      formats: ["iife"],
    },
    outDir: "dist-widget",
    emptyOutDir: true,
    minify: "esbuild",
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
});
