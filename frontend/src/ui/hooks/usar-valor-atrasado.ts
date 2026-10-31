/** Atrasa a propagação de um valor — usado para não chamar o cálculo de traço a cada tecla. */

import { useEffect, useState } from 'react'

export function usarValorAtrasado<T>(valor: T, atrasoMs = 400): T {
  const [atrasado, definirAtrasado] = useState(valor)

  useEffect(() => {
    const relogio = setTimeout(() => definirAtrasado(valor), atrasoMs)
    return () => clearTimeout(relogio)
  }, [valor, atrasoMs])

  return atrasado
}
