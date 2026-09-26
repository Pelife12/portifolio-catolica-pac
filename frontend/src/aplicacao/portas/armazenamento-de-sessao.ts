/** Porta de persistência da sessão — implementada na infraestrutura. */

export interface SessaoPersistida {
  token: string
  /** Momento de expiração em epoch ms, calculado a partir de expira_em_segundos. */
  expiraEm: number
}

export interface ArmazenamentoDeSessao {
  ler(): SessaoPersistida | null
  gravar(sessao: SessaoPersistida): void
  limpar(): void
}
