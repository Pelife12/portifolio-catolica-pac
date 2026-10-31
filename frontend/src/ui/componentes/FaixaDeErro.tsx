import type { ReactNode } from 'react'

import { Botao } from './Botao'
import { Icone } from './Icone'

interface Acao {
  texto: string
  ao: () => void
  variante?: 'primario' | 'secundario'
}

interface Props {
  titulo: string
  children: ReactNode
  acoes?: Acao[]
  tom?: 'perigo' | 'atencao'
}

/**
 * Erro contextual, no lugar onde a ação falhou — nunca um toast que desaparece:
 * no pátio, o operador pode estar olhando o termômetro quando o aviso sobe.
 */
export function FaixaDeErro({ titulo, children, acoes = [], tom = 'perigo' }: Props) {
  return (
    <div
      className={`faixa-erro${tom === 'atencao' ? ' faixa-erro--atencao' : ''}`}
      role="alert"
    >
      <div className="faixa-erro__titulo">
        <Icone nome="alerta" />
        <span>{titulo}</span>
      </div>
      <p className="faixa-erro__texto">{children}</p>
      {acoes.length > 0 ? (
        <div className="faixa-erro__acoes">
          {acoes.map((acao) => (
            <Botao
              key={acao.texto}
              variante={acao.variante ?? 'secundario'}
              onClick={acao.ao}
              style={{ flex: 1 }}
            >
              {acao.texto}
            </Botao>
          ))}
        </div>
      ) : null}
    </div>
  )
}
