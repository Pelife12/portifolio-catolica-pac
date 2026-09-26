import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    // Exposto na rede local para testar no celular dentro do pátio.
    host: true,
  },
  test: {
    // As regras testadas são puras: não precisam de DOM.
    environment: 'node',
    globals: true,
    include: ['src/**/*.teste.ts'],
  },
})
