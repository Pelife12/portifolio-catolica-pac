import type { HTMLAttributes, ReactNode } from 'react'

type Tom = 'normal' | 'atencao' | 'critico'

interface Props extends HTMLAttributes<HTMLDivElement> {
  tom?: Tom
  compacto?: boolean
  children: ReactNode
}

const CLASSE_POR_TOM: Record<Tom, string> = {
  normal: '',
  atencao: 'cartao--atencao',
  critico: 'cartao--critico',
}

export function Cartao({ tom = 'normal', compacto = false, className, children, ...resto }: Props) {
  const classes = ['cartao', CLASSE_POR_TOM[tom], compacto ? 'cartao--compacto' : '', className ?? '']
    .filter(Boolean)
    .join(' ')

  return (
    <div className={classes} {...resto}>
      {children}
    </div>
  )
}
