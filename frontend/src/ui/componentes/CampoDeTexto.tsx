import { useId, type InputHTMLAttributes } from 'react'

interface Props extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  rotulo: string
  auxiliar?: string
  erro?: string | null
  /** Caixa curta e monoespaçada, para leituras numéricas. */
  numerico?: boolean
  sufixo?: string
}

export function CampoDeTexto({
  rotulo,
  auxiliar,
  erro,
  numerico = false,
  sufixo,
  className,
  ...resto
}: Props) {
  const id = useId()
  const idAuxiliar = `${id}-auxiliar`
  const mensagem = erro ?? auxiliar

  return (
    <div className="campo">
      <label className="rotulo" htmlFor={id}>
        {rotulo}
      </label>
      <div className="campo__linha">
        <input
          id={id}
          className={[
            'campo__controle',
            numerico ? 'campo__controle--numerico' : '',
            className ?? '',
          ]
            .filter(Boolean)
            .join(' ')}
          aria-invalid={erro ? true : undefined}
          aria-describedby={mensagem ? idAuxiliar : undefined}
          {...resto}
        />
        {sufixo ? <span className="texto-secundario">{sufixo}</span> : null}
      </div>
      {mensagem ? (
        <p
          id={idAuxiliar}
          className={`campo__auxiliar${erro ? ' campo__auxiliar--erro' : ''}`}
          // Erro de campo é anunciado assim que aparece.
          role={erro ? 'alert' : undefined}
        >
          {mensagem}
        </p>
      ) : null}
    </div>
  )
}
