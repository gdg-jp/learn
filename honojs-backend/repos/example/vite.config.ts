import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "dist/public",
    emptyOutDir: true
  },
  server: {
    proxy: {
      "/api": "http://localhost:3000"
    }
  }
});
