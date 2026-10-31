import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { usarAutenticado } from '@/aplicacao/hooks/usar-sessao'

import { CAMINHOS } from './caminhos'

/**
 * Barreira de autenticação. Guarda de onde o operador veio para devolvê-lo à
 * mesma tela depois do login — no meio de uma coleta, voltar para a lista de
 * leiras seria perder o contexto.
 */
export function RotaProtegida() {
  const autenticado = usarAutenticado()
  const localizacao = useLocation()

  if (!autenticado) {
    return <Navigate to={CAMINHOS.login} replace state={{ de: localizacao.pathname }} />
  }

  return <Outlet />
}
