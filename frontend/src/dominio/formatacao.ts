/** Formatações pt-BR usadas nas telas e no histórico. */

const FUSO = 'America/Sao_Paulo'

export function formatarDataHora(iso: string): string {
  return new Date(iso).toLocaleString('pt-BR', {
    timeZone: FUSO,
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatarData(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    timeZone: FUSO,
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatarHora(iso: string): string {
  return new Date(iso).toLocaleTimeString('pt-BR', {
    timeZone: FUSO,
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatarNumero(valor: number | string, casas = 2): string {
  const numero = typeof valor === 'string' ? Number(valor) : valor
  if (!Number.isFinite(numero)) return '—'
  return numero.toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  })
}

/** Massas aparecem sem decimais quando são inteiras (1.240 kg). */
export function formatarMassa(valor: number | string): string {
  const numero = typeof valor === 'string' ? Number(valor) : valor
  if (!Number.isFinite(numero)) return '—'
  const casas = Number.isInteger(numero) ? 0 : 1
  return `${numero.toLocaleString('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  })} kg`
}

export function formatarCoordenada(latitude: number | string, longitude: number | string): string {
  return `${Number(latitude).toFixed(5)}, ${Number(longitude).toFixed(5)}`
}

/** Dias corridos desde a montagem — o "Dia 6" que aparece no cabeçalho da leira. */
export function diasDesde(iso: string, agora: Date = new Date()): number {
  const inicio = new Date(iso).getTime()
  const decorrido = agora.getTime() - inicio
  return Math.max(0, Math.floor(decorrido / 86_400_000))
}

export function horasDesde(iso: string, agora: Date = new Date()): number {
  const decorrido = agora.getTime() - new Date(iso).getTime()
  return Math.max(0, decorrido / 3_600_000)
}
