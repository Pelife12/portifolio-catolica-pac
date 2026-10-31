import { describe, expect, it } from 'vitest'

import { avaliarJanela, dentroDaJanela, explicarJanela } from './janela-temporal'

const AGORA = new Date('2026-09-24T12:00:00-03:00')

function horasAtras(horas: number): Date {
  return new Date(AGORA.getTime() - horas * 3_600_000)
}

describe('avaliarJanela (RF02 no cliente)', () => {
  it('aceita coleta recente', () => {
    expect(avaliarJanela(horasAtras(2), AGORA)).toBe('dentro')
  })

  it('aceita coleta na borda das 24 horas', () => {
    expect(avaliarJanela(horasAtras(24), AGORA)).toBe('dentro')
  })

  it('recusa coleta mais antiga que a janela', () => {
    expect(avaliarJanela(horasAtras(24.5), AGORA)).toBe('retroativa')
  })

  it('recusa coleta com data futura', () => {
    expect(avaliarJanela(horasAtras(-1), AGORA)).toBe('futura')
  })

  it('tolera pequena diferença de relógio entre aparelho e servidor', () => {
    expect(avaliarJanela(horasAtras(-0.05), AGORA)).toBe('dentro')
  })
})

describe('dentroDaJanela', () => {
  it('resume a avaliação em booleano', () => {
    expect(dentroDaJanela(horasAtras(1), AGORA)).toBe(true)
    expect(dentroDaJanela(horasAtras(48), AGORA)).toBe(false)
  })
})

describe('explicarJanela', () => {
  it('só explica quando há problema', () => {
    expect(explicarJanela('dentro')).toBeNull()
    expect(explicarJanela('retroativa')).toContain('24 horas')
    expect(explicarJanela('futura')).toContain('relógio')
  })
})
