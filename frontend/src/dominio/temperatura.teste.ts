import { describe, expect, it } from 'vitest'

import { TEMPERATURA_MAXIMA, TEMPERATURA_MINIMA } from './faixas'
import {
  ajustarTemperatura,
  classificarTemperatura,
  formatarTemperatura,
  interpretarTemperaturaDigitada,
} from './temperatura'

describe('ajustarTemperatura', () => {
  it('anda meio grau por passo', () => {
    expect(ajustarTemperatura(58, 1)).toBe(58.5)
    expect(ajustarTemperatura(58, -1)).toBe(57.5)
  })

  it('não acumula erro de ponto flutuante ao longo de muitos toques', () => {
    let valor = 0.1
    for (let i = 0; i < 40; i += 1) valor = ajustarTemperatura(valor, 1)
    expect(valor).toBe(20.1)
  })

  it('respeita os limites aceitos pela API', () => {
    expect(ajustarTemperatura(TEMPERATURA_MAXIMA, 1)).toBe(TEMPERATURA_MAXIMA)
    expect(ajustarTemperatura(TEMPERATURA_MINIMA, -1)).toBe(TEMPERATURA_MINIMA)
  })

  it('aceita salto de vários passos (toque longo)', () => {
    expect(ajustarTemperatura(50, 10)).toBe(55)
  })
})

describe('classificarTemperatura', () => {
  it('trata 55 °C como início da fase termofílica', () => {
    expect(classificarTemperatura(54.5)).toBe('mesofilica')
    expect(classificarTemperatura(55)).toBe('termofilica')
  })

  it('sinaliza calor excessivo a partir de 70 °C', () => {
    expect(classificarTemperatura(69.5)).toBe('termofilica')
    expect(classificarTemperatura(70)).toBe('excessiva')
  })

  it('reconhece leira fria', () => {
    expect(classificarTemperatura(12)).toBe('criogenica')
  })
})

describe('formatarTemperatura', () => {
  it('usa vírgula e uma casa decimal', () => {
    expect(formatarTemperatura(58.5)).toBe('58,5')
    expect(formatarTemperatura(61)).toBe('61,0')
  })
})

describe('interpretarTemperaturaDigitada', () => {
  it('aceita vírgula e ponto', () => {
    expect(interpretarTemperaturaDigitada('58,5')).toBe(58.5)
    expect(interpretarTemperaturaDigitada('58.5')).toBe(58.5)
  })

  it('recusa texto vazio, lixo e valores fora do limite', () => {
    expect(interpretarTemperaturaDigitada('')).toBeNull()
    expect(interpretarTemperaturaDigitada('abc')).toBeNull()
    expect(interpretarTemperaturaDigitada('500')).toBeNull()
  })
})
