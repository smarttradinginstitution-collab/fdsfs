import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [ vue(), vueDevTools() ],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      // Ignora le cartelle di output dei test per evitare cicli di ricarica
      ignored: ['**/playwright-report/**', '**/test-results/**'],
    },
  }
})
