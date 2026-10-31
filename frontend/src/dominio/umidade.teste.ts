import { describe, expect, it } from 'vitest'

import { classificarUmidade, interpretarUmidadeDigitada } from './umidade'

describe('classificarUmidade', () => {
  it('usa a faixa ideal de 50% a 60%', () => {
    expect(classificarUmidade(49.9)).toBe('seca')
    expect(classificarUmidade(50)).toBe('ideal')
    expect(classificarUmidade(60)).toBe('ideal')
    expect(classificarUmidade(60.1)).toBe('encharcada')
  })
})

describe('interpretarUmidadeDigitada', () => {
  it('aceita vírgula e o símbolo de porcentagem', () => {
    expect(interpretarUmidadeDigitada('55')).toBe(55)
    expect(interpretarUmidadeDigitada('55,5%')).toBe(55.5)
  })

  it('recusa vazio e valores fora de 0 a 100', () => {
    expect(interpretarUmidadeDigitada('')).toBeNull()
    expect(interpretarUmidadeDigitada('-1')).toBeNull()
    expect(interpretarUmidadeDigitada('101')).toBeNull()
  })
})
