import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8001',
      '/todo': 'http://localhost:8001',
      '/admin': 'http://localhost:8001',
    },
  },
})
