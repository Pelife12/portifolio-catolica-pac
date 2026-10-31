import type { ReactNode } from 'react'

import { Icone, type NomeDoIcone } from './Icone'

interface Props {
  icone?: NomeDoIcone
  titulo: string
  children?: ReactNode
  /** Toda tela vazia oferece o próximo passo, nunca só a ausência de dados. */
  acao?: ReactNode
}

export function EstadoVazio({ icone = 'leira', titulo, children, acao }: Props) {
  return (
    <div className="estado-vazio">
      <Icone nome={icone} tamanho={32} cor="var(--fg2)" />
      <p className="estado-vazio__titulo">{titulo}</p>
      {children ? <p className="estado-vazio__texto">{children}</p> : null}
      {acao}
    </div>
  )
}
