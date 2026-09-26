/** Porta de geolocalização (RNF01) — implementada pela infraestrutura. */

export interface Coordenada {
  latitude: number
  longitude: number
  /** Raio de precisão em metros, exibido ao operador. */
  precisaoMetros: number | null
  capturadoEm: Date
}

export type MotivoDaFalhaDeGps = 'permissao_negada' | 'indisponivel' | 'tempo_esgotado' | 'sem_suporte'

export class ErroDeGeolocalizacao extends Error {
  constructor(
    readonly motivo: MotivoDaFalhaDeGps,
    mensagem: string,
  ) {
    super(mensagem)
    this.name = 'ErroDeGeolocalizacao'
  }
}

export interface Localizador {
  capturar(): Promise<Coordenada>
}
