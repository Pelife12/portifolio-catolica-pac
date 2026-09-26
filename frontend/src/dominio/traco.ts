/**
 * Diagnóstico local do traço (RF01).
 *
 * O cálculo em si é do backend (POST /calculos/traco). Aqui ficam apenas as
 * leituras que a tela faz sobre o resultado: rótulo, direção do desvio e o
 * texto que orienta a correção da mistura.
 */

import { CN_IDEAL_MAXIMO, CN_IDEAL_MINIMO, UMIDADE_IDEAL_MAXIMA, UMIDADE_IDEAL_MINIMA } from './faixas'

export type DesvioDoTraco = 'abaixo' | 'ideal' | 'acima'

export function avaliarRelacaoCn(relacaoCn: number): DesvioDoTraco {
  if (relacaoCn < CN_IDEAL_MINIMO) return 'abaixo'
  if (relacaoCn > CN_IDEAL_MAXIMO) return 'acima'
  return 'ideal'
}

export function avaliarUmidadeDoTraco(umidade: number): DesvioDoTraco {
  if (umidade < UMIDADE_IDEAL_MINIMA) return 'abaixo'
  if (umidade > UMIDADE_IDEAL_MAXIMA) return 'acima'
  return 'ideal'
}

/** Orientação agronômica para corrigir a mistura antes de montar a leira. */
export function orientarCorrecaoCn(relacaoCn: number): string {
  switch (avaliarRelacaoCn(relacaoCn)) {
    case 'abaixo':
      return `C/N baixa (ideal ${CN_IDEAL_MINIMO}–${CN_IDEAL_MAXIMO}): acrescente resíduo rico em carbono, como palha ou serragem.`
    case 'acima':
      return `C/N alta (ideal ${CN_IDEAL_MINIMO}–${CN_IDEAL_MAXIMO}): acrescente resíduo rico em nitrogênio, como esterco ou restos de comida.`
    default:
      return `C/N dentro do ideal (${CN_IDEAL_MINIMO}–${CN_IDEAL_MAXIMO}).`
  }
}

export function orientarCorrecaoUmidade(umidade: number): string {
  switch (avaliarUmidadeDoTraco(umidade)) {
    case 'abaixo':
      return `Umidade abaixo da faixa (ideal ${UMIDADE_IDEAL_MINIMA}–${UMIDADE_IDEAL_MAXIMA}%): irrigue a mistura na montagem.`
    case 'acima':
      return `Umidade acima da faixa (ideal ${UMIDADE_IDEAL_MINIMA}–${UMIDADE_IDEAL_MAXIMA}%): acrescente material seco e estruturante.`
    default:
      return `Umidade dentro da faixa ideal (${UMIDADE_IDEAL_MINIMA}–${UMIDADE_IDEAL_MAXIMA}%).`
  }
}
