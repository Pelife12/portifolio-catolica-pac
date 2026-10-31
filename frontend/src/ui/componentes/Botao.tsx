import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variante = 'primario' | 'secundario' | 'perigo' | 'texto'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  /** Altura de 60px: ação principal da tela, alcançável com o polegar. */
  grande?: boolean
  bloco?: boolean
  carregando?: boolean
  children: ReactNode
}

const CLASSE_POR_VARIANTE: Record<Variante, string> = {
  primario: '',
  secundario: 'botao--secundario',
  perigo: 'botao--perigo',
  texto: 'botao--texto',
}

export function Botao({
  variante = 'primario',
  grande = false,
  bloco = false,
  carregando = false,
  disabled,
  className,
  children,
  ...resto
}: Props) {
  const classes = [
    'botao',
    CLASSE_POR_VARIANTE[variante],
    grande ? 'botao--grande' : '',
    bloco ? 'botao--bloco' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button
      type="button"
      className={classes}
      disabled={disabled || carregando}
      // Anuncia o trabalho em curso para quem usa leitor de tela.
      aria-busy={carregando || undefined}
      {...resto}
    >
      {carregando ? 'Enviando…' : children}
    </button>
  )
}
