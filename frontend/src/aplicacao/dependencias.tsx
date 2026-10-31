/**
 * Composition root do frontend — equivalente ao `api/deps.py` do backend.
 *
 * É o único lugar que instancia infraestrutura concreta (localStorage, fetch,
 * Geolocation API). Todo o resto recebe as dependências por este contexto, o
 * que mantém as telas testáveis com implementações falsas das portas.
 */

import { createContext, useContext, useMemo, type ReactNode } from 'react'

import { AfericoesApi } from '@/aplicacao/api/afericoes-api'
import { AlertasApi } from '@/aplicacao/api/alertas-api'
import { AutenticacaoApi } from '@/aplicacao/api/autenticacao-api'
import { LeirasApi } from '@/aplicacao/api/leiras-api'
import { ResiduosApi } from '@/aplicacao/api/residuos-api'
import type { ArmazenamentoDeSessao } from '@/aplicacao/portas/armazenamento-de-sessao'
import type { FilaDeAfericoes } from '@/aplicacao/portas/fila-de-afericoes'
import type { Localizador } from '@/aplicacao/portas/localizador'
import { GerenciadorDeSessao } from '@/aplicacao/sessao/gerenciador-de-sessao'
import { SincronizadorDeFila } from '@/aplicacao/sincronizacao/sincronizador-de-fila'
import { indexedDbDisponivel } from '@/infraestrutura/armazenamento/banco-local'
import { FilaEmMemoria } from '@/infraestrutura/armazenamento/fila-em-memoria'
import { FilaIndexedDb } from '@/infraestrutura/armazenamento/fila-indexeddb'
import { SessaoLocalStorage } from '@/infraestrutura/armazenamento/sessao-local-storage'
import { LocalizadorDoNavegador } from '@/infraestrutura/geolocalizacao/localizador-do-navegador'
import { ClienteHttp } from '@/infraestrutura/http/cliente-http'

export interface Dependencias {
  sessao: GerenciadorDeSessao
  localizador: Localizador
  autenticacao: AutenticacaoApi
  leiras: LeirasApi
  residuos: ResiduosApi
  afericoes: AfericoesApi
  alertas: AlertasApi
  fila: FilaDeAfericoes
  sincronizador: SincronizadorDeFila
}

const URL_API_PADRAO = 'http://localhost:8000/api/v1'

export function montarDependencias(
  sobrescritas: Partial<{
    urlBase: string
    armazenamento: ArmazenamentoDeSessao
    localizador: Localizador
    fila: FilaDeAfericoes
  }> = {},
): Dependencias {
  const armazenamento = sobrescritas.armazenamento ?? new SessaoLocalStorage()
  const sessao = new GerenciadorDeSessao(armazenamento)

  const http = new ClienteHttp({
    urlBase: sobrescritas.urlBase ?? import.meta.env.VITE_API_URL ?? URL_API_PADRAO,
    obterToken: sessao.obterToken,
    // 401 vindo da API significa token inválido ou expirado: derruba a sessão
    // e a RotaProtegida devolve o operador para o login.
    aoExpirarSessao: sessao.encerrar,
  })

  const afericoes = new AfericoesApi(http)
  // Sem IndexedDB a fila vive só na memória da aba: pior que persistir, melhor que perder.
  const fila =
    sobrescritas.fila ?? (indexedDbDisponivel() ? new FilaIndexedDb() : new FilaEmMemoria())

  return {
    sessao,
    localizador: sobrescritas.localizador ?? new LocalizadorDoNavegador(),
    autenticacao: new AutenticacaoApi(http),
    leiras: new LeirasApi(http),
    residuos: new ResiduosApi(http),
    afericoes,
    alertas: new AlertasApi(http),
    fila,
    sincronizador: new SincronizadorDeFila(fila, afericoes),
  }
}

const ContextoDeDependencias = createContext<Dependencias | null>(null)

export function ProvedorDeDependencias({
  children,
  dependencias,
}: {
  children: ReactNode
  dependencias?: Dependencias
}) {
  // Sem `dependencias` explícitas, monta as reais uma única vez por aplicação.
  const valor = useMemo(() => dependencias ?? montarDependencias(), [dependencias])
  return (
    <ContextoDeDependencias.Provider value={valor}>{children}</ContextoDeDependencias.Provider>
  )
}

export function usarDependencias(): Dependencias {
  const dependencias = useContext(ContextoDeDependencias)
  if (!dependencias) {
    throw new Error('usarDependencias() exige o ProvedorDeDependencias na árvore.')
  }
  return dependencias
}
