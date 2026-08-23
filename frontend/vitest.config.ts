import { defineConfig } from "vitest/config";

/** Vitest configuration with a jsdom environment for React component tests. */
export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/setupTests.ts"],
  },
});
