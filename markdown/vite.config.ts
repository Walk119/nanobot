import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000', // 您的后端地址
      changeOrigin: true,
    }
  }
}
})
