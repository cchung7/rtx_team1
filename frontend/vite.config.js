/*
Proxy - Port 5173 --> 5001
*/
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    proxy: {
      '/aqi': { target: "http://localhost:5001", changeOrigin: true, },
      '/model': { target: 'http://localhost:5001', changeOrigin: true },
      '/health': { target: 'http://localhost:5001', changeOrigin: true },
      '/categories': { target: 'http://localhost:5001', changeOrigin: true },
      '/counties': { target: 'http://localhost:5001', changeOrigin: true },
      '/refresh': { target: 'http://localhost:5001', changeOrigin: true },
    },
  },
})
