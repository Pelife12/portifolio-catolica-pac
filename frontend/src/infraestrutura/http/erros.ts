/** Erros da borda HTTP, traduzidos para algo que a tela saiba exibir. */

import { JANELA_RETROATIVA_HORAS } from '@/dominio/faixas'

export class ErroDeApi extends Error {
  constructor(
    readonly status: number,
    readonly codigo: string,
    mensagem: string,
  ) {
    super(mensagem)
    this.name = 'ErroDeApi'
  }

  get naoAutenticado(): boolean {
    return this.status === 401
  }

  get semPermissao(): boolean {
    return this.status === 403
  }

  get naoEncontrado(): boolean {
    return this.status === 404
  }

  /**
   * RF02: a coleta foi recusada pela trava de 24h (validação da API ou a
   * constraint do banco). A tela trata esse caso separadamente dos demais 422,
   * porque a ação do operador é diferente: conferir o relógio do aparelho.
   */
  get travaTemporal(): boolean {
    if (this.codigo === 'AfericaoForaDaJanela') return true
    return (
      this.status === 422 &&
      /trava|retroativ|24\s*h|janela/i.test(this.message)
    )
  }
}

/** Sem rede, DNS ou servidor fora: nada chegou ao backend. */
export class ErroDeRede extends Error {
  constructor(mensagem = 'Sem conexão com o servidor.') {
    super(mensagem)
    this.name = 'ErroDeRede'
  }
}

/** Texto amigável e acionável para qualquer erro que suba até a tela. */
export function descreverErro(erro: unknown): string {
  if (erro instanceof ErroDeApi) {
    if (erro.travaTemporal) {
      return `Coleta recusada pela trava de ${JANELA_RETROATIVA_HORAS} horas. Confira a data e a hora do aparelho.`
    }
    if (erro.naoAutenticado) return 'Sessão expirada. Entre novamente para continuar.'
    if (erro.semPermissao) return 'Seu perfil não tem permissão para esta ação.'
    return erro.message
  }
  if (erro instanceof ErroDeRede) {
    return 'Sem conexão com o servidor. O dado fica salvo no aparelho e sobe quando a rede voltar.'
  }
  if (erro instanceof Error && erro.message) return erro.message
  return 'Não foi possível concluir a operação.'
}
