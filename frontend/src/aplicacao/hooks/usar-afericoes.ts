/** Consulta e registro de aferições (RF02 + RNF01), com fila offline. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { Afericao, AfericaoCriar } from '@/aplicacao/contratos/tipos'
import { usarDependencias } from '@/aplicacao/dependencias'
import { novoItemDaFila, type ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { ErroDeRede } from '@/infraestrutura/http/erros'

import { chaves } from './chaves'

export function usarAfericoes(leiraId?: string) {
  const { afericoes } = usarDependencias()
  return useQuery<Afericao[]>({
    queryKey: chaves.afericoes(leiraId),
    queryFn: () => afericoes.listar(leiraId),
  })
}

/** O que aconteceu com a coleta: chegou ao servidor ou ficou no aparelho. */
export type ResultadoDoRegistro =
  | { tipo: 'enviada'; afericao: Afericao }
  | { tipo: 'na_fila'; item: ItemDaFila }

export interface PedidoDeRegistro {
  dados: AfericaoCriar
  /** Código da leira, guardado junto da coleta para a fila funcionar sem rede. */
  rotuloDaLeira: string
}

/**
 * Tenta enviar na hora; sem rede, a coleta vai para a fila do IndexedDB e sobe
 * depois. Recusa de negócio (trava de 24h, validação) não entra na fila: o
 * operador ainda está na tela e pode corrigir agora.
 */
export function usarRegistrarAfericao() {
  const { afericoes, fila } = usarDependencias()
  const cliente = useQueryClient()

  return useMutation<ResultadoDoRegistro, Error, PedidoDeRegistro>({
    mutationFn: async ({ dados, rotuloDaLeira }) => {
      try {
        return { tipo: 'enviada', afericao: await afericoes.registrar(dados) }
      } catch (erro) {
        if (!(erro instanceof ErroDeRede)) throw erro
        const item = novoItemDaFila(dados, rotuloDaLeira)
        await fila.adicionar(item)
        return { tipo: 'na_fila', item }
      }
    },
    onSuccess: (resultado) => {
      if (resultado.tipo === 'na_fila') {
        void cliente.invalidateQueries({ queryKey: chaves.fila })
        return
      }
      void cliente.invalidateQueries({ queryKey: chaves.afericoes(resultado.afericao.leira_id) })
      void cliente.invalidateQueries({ queryKey: chaves.afericoes() })
      // O motor roda no servidor a cada coleta nova (RF03): os alertas da leira
      // podem ter mudado.
      void cliente.invalidateQueries({ queryKey: ['alertas'] })
    },
  })
}
