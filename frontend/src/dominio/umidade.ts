/** Regras puras do campo de umidade. */

import { UMIDADE_IDEAL_MAXIMA, UMIDADE_IDEAL_MINIMA } from './faixas'

export type SituacaoDaUmidade = 'seca' | 'ideal' | 'encharcada'

export function classificarUmidade(percentual: number): SituacaoDaUmidade {
  if (percentual < UMIDADE_IDEAL_MINIMA) return 'seca'
  if (percentual > UMIDADE_IDEAL_MAXIMA) return 'encharcada'
  return 'ideal'
}

const DESCRICOES: Record<SituacaoDaUmidade, string> = {
  seca: 'abaixo da faixa · irrigar a leira',
  ideal: 'dentro da faixa ideal',
  encharcada: 'acima da faixa · revirar para aerar',
}

export function descreverUmidade(percentual: number): string {
  return DESCRICOES[classificarUmidade(percentual)]
}

/** Interpreta o texto digitado; null quando vazio ou fora de 0–100. */
export function interpretarUmidadeDigitada(texto: string): number | null {
  const limpo = texto.trim().replace(',', '.').replace('%', '')
  if (limpo === '') return null
  const valor = Number(limpo)
  if (!Number.isFinite(valor) || valor < 0 || valor > 100) return null
  return valor
}
