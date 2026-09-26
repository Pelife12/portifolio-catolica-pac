import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
// defineConfig vem do vitest para o bloco `test` ser reconhecido nos tipos.
import { defineConfig } from 'vitest/config'

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
