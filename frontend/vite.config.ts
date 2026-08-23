import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/** Vite configuration for the React application. */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "0.0.0.0",
  },
});
