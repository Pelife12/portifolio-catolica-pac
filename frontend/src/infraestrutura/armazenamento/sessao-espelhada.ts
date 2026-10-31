/**
 * Sessão espelhada no IndexedDB.
 *
 * O Service Worker não lê localStorage. Para o Background Sync conseguir
 * autenticar o envio da fila com o app fechado, o token (e a URL da API) é
 * copiado para a store `credencial`. O localStorage continua sendo a fonte da
 * página; o espelho é só para o SW, e some junto no logout.
 */

import type {
  ArmazenamentoDeSessao,
  SessaoPersistida,
} from '@/aplicacao/portas/armazenamento-de-sessao'

import { operar, STORE_CREDENCIAL } from './banco-local'

const CHAVE = 'sessao'

export class SessaoEspelhadaNoBancoLocal implements ArmazenamentoDeSessao {
  constructor(
    private readonly principal: ArmazenamentoDeSessao,
    private readonly urlBase: string,
  ) {}

  ler(): SessaoPersistida | null {
    const sessao = this.principal.ler()
    // Sessões anteriores a esta versão ainda não tinham espelho: cria agora.
    if (sessao) this.espelhar(sessao)
    return sessao
  }

  gravar(sessao: SessaoPersistida): void {
    this.principal.gravar(sessao)
    this.espelhar(sessao)
  }

  limpar(): void {
    this.principal.limpar()
    void operar(STORE_CREDENCIAL, 'readwrite', (store) => store.delete(CHAVE)).catch(() => undefined)
  }

  private espelhar(sessao: SessaoPersistida): void {
    void operar(STORE_CREDENCIAL, 'readwrite', (store) =>
      store.put({ ...sessao, urlBase: this.urlBase }, CHAVE),
    ).catch(() => undefined)
  }
}
