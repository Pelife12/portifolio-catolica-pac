import { useId, type SelectHTMLAttributes } from 'react'

export interface OpcaoDoSeletor {
  valor: string
  texto: string
}

interface Props extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'id' | 'children'> {
  rotulo: string
  opcoes: OpcaoDoSeletor[]
  auxiliar?: string
  textoVazio?: string
}

export function Seletor({ rotulo, opcoes, auxiliar, textoVazio, className, ...resto }: Props) {
  const id = useId()

  return (
    <div className="campo">
      <label className="rotulo" htmlFor={id}>
        {rotulo}
      </label>
      <select id={id} className={['campo__controle', className ?? ''].join(' ')} {...resto}>
        {textoVazio ? <option value="">{textoVazio}</option> : null}
        {opcoes.map((opcao) => (
          <option key={opcao.valor} value={opcao.valor}>
            {opcao.texto}
          </option>
        ))}
      </select>
      {auxiliar ? <p className="campo__auxiliar">{auxiliar}</p> : null}
    </div>
  )
}
