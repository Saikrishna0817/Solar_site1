import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // ponytail: dev-only proxy kills CORS hack; restrict origins in FastAPI for prod.
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
