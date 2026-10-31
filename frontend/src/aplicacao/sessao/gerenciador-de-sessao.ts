/**
 * Guarda da sessão, fora do React.
 *
 * Ficar fora da árvore resolve a dependência circular do cliente HTTP: ele
 * precisa do token para toda requisição e precisa derrubar a sessão no 401,
 * mas não pode depender de um componente. Os componentes se inscrevem via
 * `useSyncExternalStore`.
 */

import type {
  ArmazenamentoDeSessao,
  SessaoPersistida,
} from '@/aplicacao/portas/armazenamento-de-sessao'
import type { Token } from '@/aplicacao/contratos/tipos'

type Ouvinte = () => void

export class GerenciadorDeSessao {
  private estado: SessaoPersistida | null
  private readonly ouvintes = new Set<Ouvinte>()

  constructor(private readonly armazenamento: ArmazenamentoDeSessao) {
    this.estado = armazenamento.ler()
  }

  obterToken = (): string | null => {
    // Revalida a expiração a cada leitura: a aba pode ter ficado horas aberta.
    if (this.estado && this.estado.expiraEm <= Date.now()) this.encerrar()
    return this.estado?.token ?? null
  }

  get autenticado(): boolean {
    return this.obterToken() !== null
  }

  /** Grava o token recém-emitido, convertendo a validade relativa em absoluta. */
  iniciar = (token: Token): void => {
    this.estado = {
      token: token.access_token,
      expiraEm: Date.now() + token.expira_em_segundos * 1000,
    }
    this.armazenamento.gravar(this.estado)
    this.notificar()
  }

  encerrar = (): void => {
    if (this.estado === null) return
    this.estado = null
    this.armazenamento.limpar()
    this.notificar()
  }

  inscrever = (ouvinte: Ouvinte): (() => void) => {
    this.ouvintes.add(ouvinte)
    return () => this.ouvintes.delete(ouvinte)
  }

  /** Referência estável para o useSyncExternalStore comparar. */
  instantaneo = (): SessaoPersistida | null => this.estado

  private notificar(): void {
    for (const ouvinte of this.ouvintes) ouvinte()
  }
}
