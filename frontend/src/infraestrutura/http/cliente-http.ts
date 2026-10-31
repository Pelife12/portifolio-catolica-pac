/**
 * Cliente HTTP da API v1.
 *
 * Única porta de saída da aplicação para a rede: concentra a URL base, o
 * cabeçalho de autorização, a tradução de erro e o timeout. Nenhuma tela chama
 * `fetch` diretamente.
 */

import type { CorpoDeErro } from '@/aplicacao/contratos/tipos'

import { ErroDeApi, ErroDeRede } from './erros'

export type ProvedorDeToken = () => string | null
export type AoExpirarSessao = () => void

interface Opcoes {
  readonly urlBase: string
  readonly obterToken: ProvedorDeToken
  /** Chamado quando a API devolve 401: a tela de login é reassumida. */
  readonly aoExpirarSessao?: AoExpirarSessao
  /** RNF02: o teto de resposta do sistema é 2 s; aqui damos folga de rede. */
  readonly timeoutMs?: number
}

interface Requisicao {
  metodo?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  corpo?: unknown
  /** Envia como application/x-www-form-urlencoded (exigido pelo /auth/login). */
  formulario?: Record<string, string>
  parametros?: Record<string, string | number | undefined | null>
  /** Requisições públicas (login) não anexam o token. */
  publico?: boolean
}

const TIMEOUT_PADRAO_MS = 15_000

export class ClienteHttp {
  constructor(private readonly opcoes: Opcoes) {}

  async requisitar<T>(caminho: string, requisicao: Requisicao = {}): Promise<T> {
    const resposta = await this.executar(caminho, requisicao, 'application/json')
    if (resposta.status === 204) return undefined as T
    return (await resposta.json()) as T
  }

  /** Baixa um arquivo (o laudo em PDF), com o nome sugerido pelo servidor. */
  async baixar(
    caminho: string,
    requisicao: Requisicao = {},
  ): Promise<{ arquivo: Blob; nomeDoArquivo: string | null }> {
    const resposta = await this.executar(caminho, requisicao, '*/*')
    const disposicao = resposta.headers.get('Content-Disposition') ?? ''
    const nomeDoArquivo = /filename="?([^";]+)"?/i.exec(disposicao)?.[1] ?? null
    return { arquivo: await resposta.blob(), nomeDoArquivo }
  }

  private async executar(
    caminho: string,
    requisicao: Requisicao,
    aceita: string,
  ): Promise<Response> {
    const { metodo = 'GET', corpo, formulario, parametros, publico } = requisicao

    const cabecalhos = new Headers({ Accept: aceita })
    if (!publico) {
      const token = this.opcoes.obterToken()
      if (token) cabecalhos.set('Authorization', `Bearer ${token}`)
    }

    let dados: BodyInit | undefined
    if (formulario) {
      cabecalhos.set('Content-Type', 'application/x-www-form-urlencoded')
      dados = new URLSearchParams(formulario).toString()
    } else if (corpo !== undefined) {
      cabecalhos.set('Content-Type', 'application/json')
      dados = JSON.stringify(corpo)
    }

    const controlador = new AbortController()
    const relogio = setTimeout(
      () => controlador.abort(),
      this.opcoes.timeoutMs ?? TIMEOUT_PADRAO_MS,
    )

    let resposta: Response
    try {
      resposta = await fetch(this.montarUrl(caminho, parametros), {
        method: metodo,
        headers: cabecalhos,
        body: dados,
        signal: controlador.signal,
      })
    } catch {
      // Falha de transporte (offline, DNS, timeout): não houve resposta do backend.
      throw new ErroDeRede()
    } finally {
      clearTimeout(relogio)
    }

    if (!resposta.ok) throw await this.traduzirErro(resposta)
    return resposta
  }

  private montarUrl(caminho: string, parametros?: Requisicao['parametros']): string {
    const url = new URL(`${this.opcoes.urlBase.replace(/\/$/, '')}${caminho}`)
    for (const [chave, valor] of Object.entries(parametros ?? {})) {
      if (valor !== undefined && valor !== null && valor !== '') {
        url.searchParams.set(chave, String(valor))
      }
    }
    return url.toString()
  }

  private async traduzirErro(resposta: Response): Promise<ErroDeApi> {
    if (resposta.status === 401) this.opcoes.aoExpirarSessao?.()

    let codigo = `HTTP_${resposta.status}`
    let mensagem = 'Não foi possível concluir a operação.'
    try {
      const corpo = (await resposta.json()) as Partial<CorpoDeErro> & { detail?: unknown }
      if (corpo.erro) codigo = corpo.erro
      if (corpo.mensagem) {
        mensagem = corpo.mensagem
      } else if (typeof corpo.detail === 'string') {
        mensagem = corpo.detail
      } else if (Array.isArray(corpo.detail)) {
        // Erro de validação do FastAPI: junta as mensagens de cada campo.
        mensagem = corpo.detail
          .map((item) => (item as { msg?: string }).msg)
          .filter(Boolean)
          .join(' · ')
      }
    } catch {
      // Resposta sem JSON (502 de proxy, por exemplo): fica a mensagem genérica.
    }

    return new ErroDeApi(resposta.status, codigo, mensagem)
  }
}
