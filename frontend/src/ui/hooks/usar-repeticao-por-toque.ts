/**
 * Toque longo com aceleração, para os botões "+" e "−" da temperatura.
 *
 * Sem isso, subir de 42 °C para 58 °C custa 32 toques com luva. O toque longo
 * dispara em ritmo crescente até um piso de intervalo.
 */

import { useCallback, useEffect, useRef } from 'react'

const ATRASO_INICIAL_MS = 450
const INTERVALO_INICIAL_MS = 220
const INTERVALO_MINIMO_MS = 45
const FATOR_DE_ACELERACAO = 0.82

export interface RepeticaoPorToque {
  /** Repassar diretamente no elemento: cobre mouse, toque e teclado. */
  aoPressionar: () => void
  aoSoltar: () => void
}

export function usarRepeticaoPorToque(acao: () => void): RepeticaoPorToque {
  const relogio = useRef<number | null>(null)
  const intervalo = useRef(INTERVALO_INICIAL_MS)
  const acaoAtual = useRef(acao)
  acaoAtual.current = acao

  const parar = useCallback(() => {
    if (relogio.current !== null) {
      clearTimeout(relogio.current)
      relogio.current = null
    }
    intervalo.current = INTERVALO_INICIAL_MS
  }, [])

  const agendar = useCallback(
    (atraso: number) => {
      relogio.current = window.setTimeout(() => {
        acaoAtual.current()
        intervalo.current = Math.max(
          INTERVALO_MINIMO_MS,
          intervalo.current * FATOR_DE_ACELERACAO,
        )
        agendar(intervalo.current)
      }, atraso)
    },
    [],
  )

  const aoPressionar = useCallback(() => {
    // O primeiro passo é imediato; a repetição só começa depois do atraso, para
    // que um toque curto ande exatamente 0,5 °C.
    acaoAtual.current()
    parar()
    agendar(ATRASO_INICIAL_MS)
  }, [agendar, parar])

  // Solta a repetição se o componente sair da tela com o dedo ainda pressionado.
  useEffect(() => parar, [parar])

  return { aoPressionar, aoSoltar: parar }
}
