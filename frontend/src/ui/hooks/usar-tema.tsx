/**
 * Tema claro/escuro.
 *
 * O padrão segue o sistema, mas a escolha manual é respeitada e persistida: no
 * pátio ao meio-dia o claro é mais legível; no galpão à noite, o escuro.
 */

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

export type Tema = 'claro' | 'escuro'

const CHAVE = 'aferra.tema'

interface ContextoDeTema {
  tema: Tema
  alternar: () => void
}

const Contexto = createContext<ContextoDeTema | null>(null)

function temaInicial(): Tema {
  try {
    const salvo = localStorage.getItem(CHAVE)
    if (salvo === 'claro' || salvo === 'escuro') return salvo
  } catch {
    // Armazenamento bloqueado: cai na preferência do sistema.
  }
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'escuro' : 'claro'
}

export function ProvedorDeTema({ children }: { children: ReactNode }) {
  const [tema, definirTema] = useState<Tema>(temaInicial)

  useEffect(() => {
    document.documentElement.dataset.tema = tema
    try {
      localStorage.setItem(CHAVE, tema)
    } catch {
      // Sem persistência: vale só nesta sessão.
    }
  }, [tema])

  const alternar = useCallback(
    () => definirTema((atual) => (atual === 'claro' ? 'escuro' : 'claro')),
    [],
  )

  return <Contexto.Provider value={{ tema, alternar }}>{children}</Contexto.Provider>
}

export function usarTema(): ContextoDeTema {
  const contexto = useContext(Contexto)
  if (!contexto) throw new Error('usarTema() exige o ProvedorDeTema na árvore.')
  return contexto
}
