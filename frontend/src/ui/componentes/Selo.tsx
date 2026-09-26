import type { ReactNode } from 'react'

export type TomDoSelo = 'neutro' | 'ok' | 'atencao' | 'perigo' | 'acento'

interface Props {
  tom?: TomDoSelo
  children: ReactNode
}

/** Etiqueta curta de estado. O tom nunca é a única pista: sempre acompanha texto. */
export function Selo({ tom = 'neutro', children }: Props) {
  return <span className={`selo selo--${tom}`}>{children}</span>
}
