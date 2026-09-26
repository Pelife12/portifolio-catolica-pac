import { describe, expect, it } from 'vitest'

import { resumirCiclo, type LeituraDoCiclo } from './ciclo'

const MONTAGEM = new Date('2026-10-01T09:00:00-03:00')

function leitura(horasDepoisDaMontagem: number, temperatura: number): LeituraDoCiclo {
  return {
    temperatura,
    registradoEm: new Date(MONTAGEM.getTime() + horasDepoisDaMontagem * 3_600_000),
  }
}

describe('resumirCiclo', () => {
  it('descreve leira sem coleta dentro do prazo', () => {
    const resumo = resumirCiclo([], MONTAGEM, leitura(10, 0).registradoEm)
    expect(resumo.totalDeColetas).toBe(0)
    expect(resumo.ultimaLeitura).toBeNull()
    expect(resumo.prazoTermofilicoVencido).toBe(false)
  })

  it('aponta prazo vencido quando passam 72h sem coleta', () => {
    const resumo = resumirCiclo([], MONTAGEM, leitura(80, 0).registradoEm)
    expect(resumo.prazoTermofilicoVencido).toBe(true)
  })

  it('reconhece a fase termofílica atingida no prazo', () => {
    const resumo = resumirCiclo(
      [leitura(12, 42), leitura(48, 57.5)],
      MONTAGEM,
      leitura(50, 0).registradoEm,
    )
    expect(resumo.atingiuTermofilica).toBe(true)
    expect(resumo.termofilicaNoPrazo).toBe(true)
    expect(resumo.prazoTermofilicoVencido).toBe(false)
    expect(resumo.pico).toBe(57.5)
  })

  it('não considera no prazo o aquecimento que veio depois das 72h', () => {
    const resumo = resumirCiclo(
      [leitura(24, 40), leitura(96, 58)],
      MONTAGEM,
      leitura(100, 0).registradoEm,
    )
    expect(resumo.atingiuTermofilica).toBe(true)
    expect(resumo.termofilicaNoPrazo).toBe(false)
    expect(resumo.prazoTermofilicoVencido).toBe(true)
  })

  it('detecta queda brusca de 10 °C entre coletas consecutivas', () => {
    const resumo = resumirCiclo(
      [leitura(24, 62), leitura(48, 51)],
      MONTAGEM,
      leitura(50, 0).registradoEm,
    )
    expect(resumo.quedaBrusca).toBe(true)
  })

  it('não confunde oscilação pequena com queda brusca', () => {
    const resumo = resumirCiclo(
      [leitura(24, 62), leitura(48, 56)],
      MONTAGEM,
      leitura(50, 0).registradoEm,
    )
    expect(resumo.quedaBrusca).toBe(false)
  })

  it('ordena o histórico antes de ler, aceitando qualquer ordem de entrada', () => {
    const resumo = resumirCiclo(
      [leitura(48, 58), leitura(12, 40)],
      MONTAGEM,
      leitura(50, 0).registradoEm,
    )
    expect(resumo.ultimaLeitura?.temperatura).toBe(58)
    expect(resumo.horasSemColeta).toBeCloseTo(2, 5)
  })
})
