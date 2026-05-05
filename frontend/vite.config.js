import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API requests to the backend to avoid CORS and cookie SameSite issues during development
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        ws: false,
      },
    },
  }
});
