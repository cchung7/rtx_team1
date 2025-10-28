/*
CORS proxy - Port 5173 --> 5001
*/
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    proxy: {
      '/api': {
        target: "http://localhost:5001",
        changeOrigin: true,
      },
    },
  },
})
