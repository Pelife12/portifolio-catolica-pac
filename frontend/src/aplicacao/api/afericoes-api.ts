/** Chamadas de aferição (RF02 + RNF01). */

import type { Afericao, AfericaoCriar } from '@/aplicacao/contratos/tipos'
import type { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export class AfericoesApi {
  constructor(private readonly http: ClienteHttp) {}

  /**
   * Registra a coleta. A API responde 201 quando cria e 200 quando o
   * `id_cliente` já existia — nos dois casos o corpo é a aferição, o que torna
   * o reenvio seguro (idempotência da sincronização offline).
   */
  registrar(dados: AfericaoCriar): Promise<Afericao> {
    return this.http.requisitar<Afericao>('/afericoes', { metodo: 'POST', corpo: dados })
  }

  listar(leiraId?: string, limite = 200): Promise<Afericao[]> {
    return this.http.requisitar<Afericao[]>('/afericoes', {
      parametros: { leira_id: leiraId, limite },
    })
  }
}
