/** Base de conhecimento de resíduos. */

import type { Residuo } from '@/aplicacao/contratos/tipos'
import type { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export class ResiduosApi {
  constructor(private readonly http: ClienteHttp) {}

  listar(): Promise<Residuo[]> {
    return this.http.requisitar<Residuo[]>('/residuos', { parametros: { limite: 500 } })
  }
}
