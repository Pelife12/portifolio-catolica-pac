/** Estado de autenticação e os casos de uso de entrar/sair. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useSyncExternalStore } from 'react'

import { usarDependencias } from '@/aplicacao/dependencias'
import type { Usuario } from '@/aplicacao/contratos/tipos'

import { chaves } from './chaves'

export function usarAutenticado(): boolean {
  const { sessao } = usarDependencias()
  const instantaneo = useSyncExternalStore(sessao.inscrever, sessao.instantaneo)
  return instantaneo !== null
}

export function usarUsuarioAtual() {
  const { autenticacao } = usarDependencias()
  const autenticado = usarAutenticado()

  return useQuery<Usuario>({
    queryKey: chaves.usuarioAtual,
    queryFn: () => autenticacao.eu(),
    enabled: autenticado,
    staleTime: 5 * 60 * 1000,
  })
}

export function usarEntrar() {
  const { autenticacao, sessao } = usarDependencias()
  const cliente = useQueryClient()

  return useMutation({
    mutationFn: ({ email, senha }: { email: string; senha: string }) =>
      autenticacao.entrar(email, senha),
    onSuccess: (token) => {
      sessao.iniciar(token)
      // Some com o cache do usuário anterior antes de buscar o novo.
      void cliente.invalidateQueries({ queryKey: chaves.usuarioAtual })
    },
  })
}

export function usarSair(): () => void {
  const { sessao } = usarDependencias()
  const cliente = useQueryClient()

  return useCallback(() => {
    sessao.encerrar()
    // Limpa todo o cache: os dados são de uma usina e de um usuário específicos.
    cliente.clear()
  }, [cliente, sessao])
}
