import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Widget builds ChatBot + React into a single self-contained IIFE bundle.
// No iframe — the chatbot renders directly into the host page.
export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: path.resolve(__dirname, "widget/widget.tsx"),
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
    cssCodeSplit: false,
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
});
