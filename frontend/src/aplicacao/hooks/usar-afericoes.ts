/** Consulta e registro de aferições (RF02 + RNF01). */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type { Afericao, AfericaoCriar } from '@/aplicacao/contratos/tipos'
import { usarDependencias } from '@/aplicacao/dependencias'
import { ErroDeApi } from '@/infraestrutura/http/erros'

import { chaves } from './chaves'

export function usarAfericoes(leiraId?: string) {
  const { afericoes } = usarDependencias()
  return useQuery<Afericao[]>({
    queryKey: chaves.afericoes(leiraId),
    queryFn: () => afericoes.listar(leiraId),
  })
}

export function usarRegistrarAfericao() {
  const { afericoes } = usarDependencias()
  const cliente = useQueryClient()

  return useMutation<Afericao, Error, AfericaoCriar>({
    mutationFn: (dados) => afericoes.registrar(dados),
    // Trava de 24h e validação são decisões de negócio: repetir não muda o
    // resultado. Só vale insistir em falha de transporte, e disso cuida a
    // política global do QueryClient.
    retry: (tentativas, erro) => !(erro instanceof ErroDeApi) && tentativas < 2,
    onSuccess: (afericao) => {
      void cliente.invalidateQueries({ queryKey: chaves.afericoes(afericao.leira_id) })
      void cliente.invalidateQueries({ queryKey: chaves.afericoes() })
      // O motor roda no servidor a cada coleta nova (RF03): os alertas da leira
      // podem ter mudado.
      void cliente.invalidateQueries({ queryKey: ['alertas'] })
    },
  })
}
