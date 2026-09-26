/** Consultas e mutações de leiras. */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type {
  ItemDeComposicao,
  Leira,
  LeiraCriar,
  ResultadoDoTraco,
} from '@/aplicacao/contratos/tipos'
import { usarDependencias } from '@/aplicacao/dependencias'

import { chaves } from './chaves'

export function usarLeiras(usinaId?: string) {
  const { leiras } = usarDependencias()
  return useQuery<Leira[]>({
    queryKey: chaves.leiras(usinaId),
    queryFn: () => leiras.listar(usinaId),
  })
}

export function usarLeira(leiraId: string | undefined) {
  const { leiras } = usarDependencias()
  return useQuery<Leira>({
    queryKey: chaves.leira(leiraId ?? ''),
    queryFn: () => leiras.obter(leiraId as string),
    enabled: Boolean(leiraId),
  })
}

export function usarComposicaoDaLeira(leiraId: string | undefined) {
  const { leiras } = usarDependencias()
  return useQuery({
    queryKey: chaves.composicao(leiraId ?? ''),
    queryFn: () => leiras.listarComposicao(leiraId as string),
    enabled: Boolean(leiraId),
  })
}

/**
 * Cadastro completo da leira: cria e, havendo composição, grava o traço na
 * sequência. São duas chamadas porque o backend separa identificação (POST
 * /leiras) de composição (PUT /leiras/{id}/composicao); a segunda devolve a
 * leira já com relação C/N e umidade iniciais persistidas.
 */
export function usarCriarLeira() {
  const { leiras } = usarDependencias()
  const cliente = useQueryClient()

  return useMutation({
    mutationFn: async ({
      dados,
      itens,
    }: {
      dados: LeiraCriar
      itens: ItemDeComposicao[]
    }): Promise<Leira> => {
      const leira = await leiras.criar(dados)
      if (itens.length === 0) return leira
      return leiras.definirComposicao(leira.id, itens)
    },
    onSuccess: (leira) => {
      void cliente.invalidateQueries({ queryKey: ['leiras'] })
      cliente.setQueryData(chaves.leira(leira.id), leira)
    },
  })
}

/** Cálculo avulso do traço (RF01) para o retorno em tempo real na tela. */
export function usarCalcularTraco() {
  const { leiras } = usarDependencias()
  return useMutation<ResultadoDoTraco, Error, ItemDeComposicao[]>({
    mutationFn: (itens) => leiras.calcularTraco(itens),
  })
}
