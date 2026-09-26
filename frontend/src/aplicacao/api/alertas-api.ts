/** Chamadas do motor de inferência e dos alertas (RF03). */

import type { Alerta, StatusAlerta } from '@/aplicacao/contratos/tipos'
import type { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export class AlertasApi {
  constructor(private readonly http: ClienteHttp) {}

  listar(filtros: { leiraId?: string; status?: StatusAlerta } = {}): Promise<Alerta[]> {
    return this.http.requisitar<Alerta[]>('/alertas', {
      parametros: { leira_id: filtros.leiraId, status: filtros.status, limite: 300 },
    })
  }

  reconhecer(alertaId: string): Promise<Alerta> {
    return this.http.requisitar<Alerta>(`/alertas/${alertaId}/reconhecer`, {
      metodo: 'POST',
    })
  }

  resolver(alertaId: string): Promise<Alerta> {
    return this.http.requisitar<Alerta>(`/alertas/${alertaId}/resolver`, { metodo: 'POST' })
  }

  /** Roda o motor termofílico sob demanda e devolve os alertas gerados. */
  avaliarLeira(leiraId: string): Promise<Alerta[]> {
    return this.http.requisitar<Alerta[]>(`/leiras/${leiraId}/avaliar`, { metodo: 'POST' })
  }
}
