import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tsConfigPaths from 'vite-tsconfig-paths';
import svgr from "vite-plugin-svgr";

import path from "path"


export default defineConfig({
  plugins: [svgr(), react(), tsConfigPaths()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    manifest: true,
    outDir: '../backend/api/static/dist',
    rollupOptions: {
      input: "src/main.tsx",
      output: {
        strict: false,
      }
    },
  }
})

