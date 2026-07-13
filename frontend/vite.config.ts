import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
  preview: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
  test: {
    exclude: ['e2e/**', 'node_modules/**'],
  },
})
