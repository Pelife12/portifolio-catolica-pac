/**
 * Indicador de rede do aparelho.
 *
 * `navigator.onLine` só garante o negativo (offline é offline); estar "online"
 * não garante que a API responde. Serve para avisar o operador, não para
 * decidir se envia — quem decide é o resultado da requisição.
 */

import { useEffect, useState } from 'react'

export function usarStatusDeRede(): boolean {
  const [online, definirOnline] = useState(() => navigator.onLine)

  useEffect(() => {
    const entrou = () => definirOnline(true)
    const saiu = () => definirOnline(false)
    window.addEventListener('online', entrou)
    window.addEventListener('offline', saiu)
    return () => {
      window.removeEventListener('online', entrou)
      window.removeEventListener('offline', saiu)
    }
  }, [])

  return online
}
