import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { App } from './App'
import { registrarServiceWorker } from './infraestrutura/pwa/service-worker'

import './estilos/tokens.css'
import './estilos/base.css'
import './estilos/componentes.css'
import './estilos/layout.css'
import './estilos/paginas.css'

const raiz = document.getElementById('raiz')
if (!raiz) throw new Error('Elemento #raiz não encontrado no index.html.')

createRoot(raiz).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Depois do primeiro render: o registro do SW não pode atrasar a abertura da tela.
void registrarServiceWorker()
