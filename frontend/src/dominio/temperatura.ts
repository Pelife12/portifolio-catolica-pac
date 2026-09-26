/** Regras puras da leitura de temperatura usada na coleta de campo. */

import {
  PASSO_TEMPERATURA,
  TEMPERATURA_MAXIMA,
  TEMPERATURA_MINIMA,
  TEMPERATURA_TERMOFILICA_MINIMA,
} from './faixas'

export type FaseDaLeitura = 'criogenica' | 'mesofilica' | 'termofilica' | 'excessiva'

/** Acima disto o excesso de calor começa a matar a microbiota desejável. */
const TEMPERATURA_EXCESSIVA = 70
const TEMPERATURA_MESOFILICA_MINIMA = 20

/**
 * Soma `passos` ao valor, mantendo-o na grade de 0,5 °C e dentro dos limites
 * aceitos pela API. Trabalha em décimos para não acumular erro de ponto
 * flutuante ao longo de dezenas de toques.
 */
export function ajustarTemperatura(valor: number, passos: number): number {
  const decimos = Math.round(valor * 10) + Math.round(PASSO_TEMPERATURA * 10) * passos
  const ajustado = decimos / 10
  if (ajustado < TEMPERATURA_MINIMA) return TEMPERATURA_MINIMA
  if (ajustado > TEMPERATURA_MAXIMA) return TEMPERATURA_MAXIMA
  return ajustado
}

export function classificarTemperatura(valor: number): FaseDaLeitura {
  if (valor >= TEMPERATURA_EXCESSIVA) return 'excessiva'
  if (valor >= TEMPERATURA_TERMOFILICA_MINIMA) return 'termofilica'
  if (valor >= TEMPERATURA_MESOFILICA_MINIMA) return 'mesofilica'
  return 'criogenica'
}

const DESCRICOES: Record<FaseDaLeitura, string> = {
  criogenica: 'leira fria · fora de atividade',
  mesofilica: 'fase mesofílica · abaixo de 55 °C',
  termofilica: 'fase termofílica · dentro da regra do MAPA',
  excessiva: 'calor excessivo · revirar a leira',
}

export function descreverTemperatura(valor: number): string {
  return DESCRICOES[classificarTemperatura(valor)]
}

/** Formata com uma casa decimal e vírgula, como o operador escreve na prancheta. */
export function formatarTemperatura(valor: number): string {
  return valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
}

/**
 * Converte o que foi digitado à mão no campo (vírgula ou ponto) em número.
 * Devolve null quando não é um número utilizável.
 */
export function interpretarTemperaturaDigitada(texto: string): number | null {
  const limpo = texto.trim().replace(',', '.')
  if (limpo === '') return null
  const valor = Number(limpo)
  if (!Number.isFinite(valor)) return null
  if (valor < TEMPERATURA_MINIMA || valor > TEMPERATURA_MAXIMA) return null
  return valor
}
