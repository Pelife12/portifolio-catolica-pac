/** Base de conhecimento de resíduos — muda pouco, cache longo. */

import { useQuery } from '@tanstack/react-query'

import type { Residuo } from '@/aplicacao/contratos/tipos'
import { usarDependencias } from '@/aplicacao/dependencias'

import { chaves } from './chaves'

export function usarResiduos() {
  const { residuos } = usarDependencias()
  return useQuery<Residuo[]>({
    queryKey: chaves.residuos,
    queryFn: () => residuos.listar(),
    staleTime: 30 * 60 * 1000,
  })
}
