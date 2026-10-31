/**
 * Limite de erro da interface.
 *
 * Uma exceção num componente não pode deixar a tela em branco no pátio: o
 * operador perderia o caminho até a fila, onde as coletas continuam salvas.
 * Mostra o que aconteceu e oferece recarregar ou voltar às leiras.
 */

import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface Estado {
  erro: Error | null
}

export class LimiteDeErro extends Component<Props, Estado> {
  state: Estado = { erro: null }

  static getDerivedStateFromError(erro: Error): Estado {
    return { erro }
  }

  componentDidCatch(erro: Error, info: ErrorInfo): void {
    console.error('Falha não tratada na interface:', erro, info.componentStack)
  }

  render() {
    if (!this.state.erro) return this.props.children

    return (
      <div className="casca-auth">
        <div className="casca-auth__caixa pilha">
          <div className="faixa-erro" role="alert">
            <div className="faixa-erro__titulo">Algo deu errado nesta tela</div>
            <p className="faixa-erro__texto">
              As coletas salvas no aparelho não foram afetadas. Recarregue o app; se o erro
              continuar, avise o gestor da usina.
            </p>
            <div className="faixa-erro__acoes">
              <button
                type="button"
                className="botao"
                style={{ flex: 1 }}
                onClick={() => window.location.reload()}
              >
                Recarregar
              </button>
              <button
                type="button"
                className="botao botao--secundario"
                style={{ flex: 1 }}
                onClick={() => window.location.assign('/leiras')}
              >
                Ir para as leiras
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
