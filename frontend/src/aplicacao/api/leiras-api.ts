/** Chamadas de leiras e da sua composição (traço). */

import type {
  ItemDaComposicaoSalva,
  ItemDeComposicao,
  Leira,
  LeiraCriar,
  ResultadoDoTraco,
} from '@/aplicacao/contratos/tipos'
import type { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export class LeirasApi {
  constructor(private readonly http: ClienteHttp) {}

  listar(usinaId?: string): Promise<Leira[]> {
    return this.http.requisitar<Leira[]>('/leiras', {
      parametros: { usina_id: usinaId, limite: 200 },
    })
  }

  obter(leiraId: string): Promise<Leira> {
    return this.http.requisitar<Leira>(`/leiras/${leiraId}`)
  }

  criar(dados: LeiraCriar): Promise<Leira> {
    return this.http.requisitar<Leira>('/leiras', { metodo: 'POST', corpo: dados })
  }

  /** Grava a composição e devolve a leira já com o traço inicial calculado. */
  definirComposicao(leiraId: string, itens: ItemDeComposicao[]): Promise<Leira> {
    return this.http.requisitar<Leira>(`/leiras/${leiraId}/composicao`, {
      metodo: 'PUT',
      corpo: { itens },
    })
  }

  listarComposicao(leiraId: string): Promise<ItemDaComposicaoSalva[]> {
    return this.http.requisitar<ItemDaComposicaoSalva[]>(`/leiras/${leiraId}/composicao`)
  }

  /** Cálculo avulso, sem persistir: alimenta o traço em tempo real na tela. */
  calcularTraco(itens: ItemDeComposicao[]): Promise<ResultadoDoTraco> {
    return this.http.requisitar<ResultadoDoTraco>('/calculos/traco', {
      metodo: 'POST',
      corpo: { itens },
    })
  }
}
