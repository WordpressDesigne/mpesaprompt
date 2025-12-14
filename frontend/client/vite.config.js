import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/signup': 'http://127.0.0.1:5000',
      '/login': 'http://127.0.0.1:5000',
      '/dashboard': 'http://127.0.0.1:5000',
      '/settings/update': 'http://127.0.0.1:5000',
      '/stk-push': 'http://127.0.0.1:5000',
      '/callback': 'http://127.0.0.1:5000',
    }
  }
})
