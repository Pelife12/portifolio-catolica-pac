/** Fila local de aferições: leitura para a tela e disparo da sincronização. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { usarDependencias } from '@/aplicacao/dependencias'
import type { ResultadoDaSincronizacao } from '@/aplicacao/sincronizacao/sincronizador-de-fila'

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
