/** Fila local de aferições: leitura para a tela e disparo da sincronização. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'

import type { ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { usarDependencias } from '@/aplicacao/dependencias'
import type { ResultadoDaSincronizacao } from '@/aplicacao/sincronizacao/sincronizador-de-fila'
import { aoPedidoDeSincronizacaoDoServiceWorker } from '@/infraestrutura/pwa/background-sync'

import { chaves } from './chaves'

export function usarFila() {
  const { fila } = usarDependencias()
  return useQuery<ItemDaFila[]>({
    queryKey: chaves.fila,
    queryFn: () => fila.listar(),
    // A fila é local: não depende de rede e deve refletir o aparelho na hora.
    networkMode: 'always',
    staleTime: 0,
  })
}

export function usarSincronizarFila() {
  const { sincronizador } = usarDependencias()
  const cliente = useQueryClient()

  return useMutation<ResultadoDaSincronizacao, Error, void>({
    mutationFn: () => sincronizador.sincronizar(),
    networkMode: 'always',
    onSettled: (resultado) => {
      void cliente.invalidateQueries({ queryKey: chaves.fila })
      if (resultado && resultado.enviadas > 0) {
        void cliente.invalidateQueries({ queryKey: ['afericoes'] })
        void cliente.invalidateQueries({ queryKey: ['alertas'] })
      }
    },
  })
}

/** Remove da fila uma coleta recusada — decisão do operador, nunca automática. */
export function usarDescartarItemDaFila() {
  const { fila } = usarDependencias()
  const cliente = useQueryClient()
  return useMutation({
    mutationFn: (idCliente: string) => fila.remover(idCliente),
    networkMode: 'always',
    onSuccess: () => void cliente.invalidateQueries({ queryKey: chaves.fila }),
  })
}

/** Devolve uma coleta recusada à fila, para quando a causa já foi resolvida. */
export function usarReenviarItemDaFila() {
  const { fila } = usarDependencias()
  const cliente = useQueryClient()
  return useMutation({
    mutationFn: (item: ItemDaFila) => fila.salvar({ ...item, estado: 'pendente' }),
    networkMode: 'always',
    onSuccess: () => void cliente.invalidateQueries({ queryKey: chaves.fila }),
  })
}

const INTERVALO_DE_TENTATIVA_MS = 60_000

/**
 * Upload silencioso (05/11): com o app aberto, a fila sobe ao abrir, ao voltar a
 * rede, quando o Service Worker pede (Background Sync) e de minuto em minuto
 * enquanto houver pendência. Com o app fechado, quem envia é o próprio SW.
 */
export function usarSincronizacaoAutomatica(): void {
  const { data: itens } = usarFila()
  const { mutate: sincronizar } = usarSincronizarFila()
  const haPendentes = (itens ?? []).some((item) => item.estado === 'pendente')

  useEffect(() => {
    const disparar = () => sincronizar()
    window.addEventListener('online', disparar)
    const pararDeOuvirSw = aoPedidoDeSincronizacaoDoServiceWorker(disparar)
    return () => {
      window.removeEventListener('online', disparar)
      pararDeOuvirSw()
    }
  }, [sincronizar])

  useEffect(() => {
    if (!haPendentes) return
    sincronizar()
    const relogio = setInterval(() => {
      if (navigator.onLine) sincronizar()
    }, INTERVALO_DE_TENTATIVA_MS)
    return () => clearInterval(relogio)
  }, [haPendentes, sincronizar])
}
