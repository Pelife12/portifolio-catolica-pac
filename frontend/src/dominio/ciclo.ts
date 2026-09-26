/**
 * Leitura do ciclo da leira a partir do histórico de aferições.
 *
 * Espelha o que o motor de inferência do backend (RF03) decide, mas com outra
 * finalidade: aqui é só para o painel explicar ao gestor o que está havendo. A
 * autoridade sobre alertas continua sendo do servidor — esta função não gera
 * alerta nenhum, apenas descreve o histórico que já chegou.
 */

import {
  PRAZO_FASE_TERMOFILICA_HORAS,
  QUEDA_BRUSCA_DELTA_CELSIUS,
  TEMPERATURA_TERMOFILICA_MINIMA,
} from './faixas'

/** Apenas o que interessa de uma aferição para a leitura do ciclo. */
export interface LeituraDoCiclo {
  temperatura: number
  registradoEm: Date
}

export interface ResumoDoCiclo {
  totalDeColetas: number
  ultimaLeitura: LeituraDoCiclo | null
  /** Maior temperatura já registrada no ciclo. */
  pico: number | null
  horasSemColeta: number | null
  /** A leira já passou de 55 °C em algum momento. */
  atingiuTermofilica: boolean
  /** Passou de 55 °C dentro das 72h seguintes à montagem. */
  termofilicaNoPrazo: boolean
  /** O prazo de 72h venceu sem a leira atingir a fase termofílica. */
  prazoTermofilicoVencido: boolean
  /** Queda de 10 °C ou mais entre duas coletas consecutivas. */
  quedaBrusca: boolean
}

/**
 * @param leituras histórico da leira, em qualquer ordem
 * @param dataMontagem início do ciclo, base do prazo de 72h
 */
export function resumirCiclo(
  leituras: LeituraDoCiclo[],
  dataMontagem: Date,
  agora: Date = new Date(),
): ResumoDoCiclo {
  const ordenadas = [...leituras].sort(
    (a, b) => a.registradoEm.getTime() - b.registradoEm.getTime(),
  )

  if (ordenadas.length === 0) {
    const horasDeCiclo = (agora.getTime() - dataMontagem.getTime()) / 3_600_000
    return {
      totalDeColetas: 0,
      ultimaLeitura: null,
      pico: null,
      horasSemColeta: null,
      atingiuTermofilica: false,
      termofilicaNoPrazo: false,
      prazoTermofilicoVencido: horasDeCiclo > PRAZO_FASE_TERMOFILICA_HORAS,
      quedaBrusca: false,
    }
  }

  const ultima = ordenadas[ordenadas.length - 1] as LeituraDoCiclo
  const pico = Math.max(...ordenadas.map((leitura) => leitura.temperatura))

  const limiteDoPrazo = new Date(
    dataMontagem.getTime() + PRAZO_FASE_TERMOFILICA_HORAS * 3_600_000,
  )
  const atingiuTermofilica = ordenadas.some(
    (leitura) => leitura.temperatura >= TEMPERATURA_TERMOFILICA_MINIMA,
  )
  const termofilicaNoPrazo = ordenadas.some(
    (leitura) =>
      leitura.temperatura >= TEMPERATURA_TERMOFILICA_MINIMA &&
      leitura.registradoEm <= limiteDoPrazo,
  )

  let quedaBrusca = false
  for (let i = 1; i < ordenadas.length; i += 1) {
    const anterior = ordenadas[i - 1] as LeituraDoCiclo
    const atual = ordenadas[i] as LeituraDoCiclo
    if (anterior.temperatura - atual.temperatura >= QUEDA_BRUSCA_DELTA_CELSIUS) {
      quedaBrusca = true
      break
    }
  }

  return {
    totalDeColetas: ordenadas.length,
    ultimaLeitura: ultima,
    pico,
    horasSemColeta: (agora.getTime() - ultima.registradoEm.getTime()) / 3_600_000,
    atingiuTermofilica,
    termofilicaNoPrazo,
    prazoTermofilicoVencido: !termofilicaNoPrazo && agora > limiteDoPrazo,
    quedaBrusca,
  }
}
