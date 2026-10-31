/**
 * RF02 no cliente: a trava de 24h é decidida pela API e pelo banco, mas a tela
 * checa antes de enviar para não deixar o operador registrar uma coleta que
 * será recusada — no pátio, descobrir isso só na sincronização é perder o dado.
 */

import { JANELA_RETROATIVA_HORAS } from './faixas'

export type SituacaoDaJanela = 'dentro' | 'retroativa' | 'futura'

export function avaliarJanela(registradoEm: Date, agora: Date = new Date()): SituacaoDaJanela {
  const diferencaHoras = (agora.getTime() - registradoEm.getTime()) / 3_600_000
  // Uma pequena folga negativa absorve a diferença de relógio entre aparelho e servidor.
  if (diferencaHoras < -0.083) return 'futura'
  if (diferencaHoras > JANELA_RETROATIVA_HORAS) return 'retroativa'
  return 'dentro'
}

export function dentroDaJanela(registradoEm: Date, agora: Date = new Date()): boolean {
  return avaliarJanela(registradoEm, agora) === 'dentro'
}

export function explicarJanela(situacao: SituacaoDaJanela): string | null {
  switch (situacao) {
    case 'retroativa':
      return `A coleta tem mais de ${JANELA_RETROATIVA_HORAS} horas e será recusada pelo servidor. Verifique a data e a hora do aparelho.`
    case 'futura':
      return 'A coleta está com data futura. Corrija o relógio do aparelho antes de registrar.'
    default:
      return null
  }
}
