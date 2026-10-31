/** Painel de alertas e ações do gestor sobre eles (RF03). */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { Alerta, StatusAlerta } from '@/aplicacao/contratos/tipos'
import { usarDependencias } from '@/aplicacao/dependencias'

import { chaves } from './chaves'

export function usarAlertas(filtros: { leiraId?: string; status?: StatusAlerta } = {}) {
  const { alertas } = usarDependencias()
  return useQuery<Alerta[]>({
    queryKey: chaves.alertas(filtros.leiraId, filtros.status),
    queryFn: () => alertas.listar(filtros),
    // O gestor deixa o painel aberto: revalida de minuto em minuto.
    refetchInterval: 60_000,
  })
}

export function usarReconhecerAlerta() {
  const { alertas } = usarDependencias()
  const cliente = useQueryClient()
  return useMutation({
    mutationFn: (alertaId: string) => alertas.reconhecer(alertaId),
    onSuccess: () => void cliente.invalidateQueries({ queryKey: ['alertas'] }),
  })
}

export function usarResolverAlerta() {
  const { alertas } = usarDependencias()
  const cliente = useQueryClient()
  return useMutation({
    mutationFn: (alertaId: string) => alertas.resolver(alertaId),
    onSuccess: () => void cliente.invalidateQueries({ queryKey: ['alertas'] }),
  })
}
