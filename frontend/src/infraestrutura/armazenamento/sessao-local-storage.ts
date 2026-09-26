/**
 * Implementação da porta de sessão sobre o localStorage.
 *
 * O token fica no localStorage porque o app precisa sobreviver ao fechamento
 * do navegador no meio do pátio — o operador não tem como refazer login sem
 * rede. Toda leitura é defensiva: em modo privado o acesso pode lançar.
 */

import type {
  ArmazenamentoDeSessao,
  SessaoPersistida,
} from '@/aplicacao/portas/armazenamento-de-sessao'

const CHAVE = 'aferra.sessao'

export class SessaoLocalStorage implements ArmazenamentoDeSessao {
  ler(): SessaoPersistida | null {
    try {
      const bruto = localStorage.getItem(CHAVE)
      if (!bruto) return null
      const sessao = JSON.parse(bruto) as SessaoPersistida
      if (typeof sessao.token !== 'string' || typeof sessao.expiraEm !== 'number') {
        return null
      }
      if (sessao.expiraEm <= Date.now()) {
        this.limpar()
        return null
      }
      return sessao
    } catch {
      return null
    }
  }

  gravar(sessao: SessaoPersistida): void {
    try {
      localStorage.setItem(CHAVE, JSON.stringify(sessao))
    } catch {
      // Armazenamento bloqueado: a sessão vale só enquanto a aba estiver aberta.
    }
  }

  limpar(): void {
    try {
      localStorage.removeItem(CHAVE)
    } catch {
      // Nada a fazer.
    }
  }
}
