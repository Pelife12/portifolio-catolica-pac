/**
 * Simulação de quebra de rede na sincronização (entrega de 19/11).
 *
 * O servidor falso reproduz o contrato da API: idempotência por id_cliente
 * (201 na primeira vez, 200 com o mesmo registro depois) e a trava de 24h.
 * A rede é derrubada à força em pontos diferentes do envio para provar que
 * nenhuma coleta se perde nem duplica.
 */

import { beforeEach, describe, expect, it } from 'vitest'

import type { Afericao, AfericaoCriar } from '@/aplicacao/contratos/tipos'
import { novoItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { FilaEmMemoria } from '@/infraestrutura/armazenamento/fila-em-memoria'
import { ErroDeApi, ErroDeRede } from '@/infraestrutura/http/erros'

import { SincronizadorDeFila, type EnvioDeAfericao } from './sincronizador-de-fila'

type Falha = 'antes_de_chegar' | 'depois_de_gravar' | null

class ServidorFalso implements EnvioDeAfericao {
  readonly gravadas = new Map<string, Afericao>()
  chamadas = 0
  /** Falhas programadas por ordem de chamada (null = chamada normal). */
  roteiro: Falha[] = []
  rejeitarIds = new Set<string>()
  sessaoExpirada = false

  async registrar(dados: AfericaoCriar): Promise<Afericao> {
    const falha = this.roteiro[this.chamadas] ?? null
    this.chamadas += 1

    if (falha === 'antes_de_chegar') throw new ErroDeRede()
    if (this.sessaoExpirada) throw new ErroDeApi(401, 'NaoAutenticado', 'Token expirado.')
    if (this.rejeitarIds.has(dados.id_cliente)) {
      throw new ErroDeApi(422, 'AfericaoForaDaJanela', 'Coleta retroativa a mais de 24 horas.')
    }

    const existente = this.gravadas.get(dados.id_cliente)
    const afericao = existente ?? paraAfericao(dados)
    this.gravadas.set(dados.id_cliente, afericao)

    // A requisição chegou e foi gravada, mas a resposta se perdeu no caminho.
    if (falha === 'depois_de_gravar') throw new ErroDeRede()
    return afericao
  }
}

function paraAfericao(dados: AfericaoCriar): Afericao {
  return {
    id: `srv-${dados.id_cliente}`,
    leira_id: dados.leira_id,
    usuario_id: 'operador',
    temperatura_celsius: String(dados.temperatura_celsius),
    umidade_percentual: dados.umidade_percentual == null ? null : String(dados.umidade_percentual),
    registrado_em: dados.registrado_em,
    latitude: String(dados.latitude),
    longitude: String(dados.longitude),
    id_cliente: dados.id_cliente,
    sincronizado_em: new Date().toISOString(),
  }
}

let contador = 0
function coleta(temperatura = 58.5): AfericaoCriar {
  contador += 1
  return {
    leira_id: 'leira-1',
    temperatura_celsius: temperatura,
    umidade_percentual: 55,
    registrado_em: new Date(Date.UTC(2026, 10, 19, 9, contador)).toISOString(),
    latitude: -26.91,
    longitude: -49.07,
    id_cliente: `cliente-${contador}`,
  }
}

async function enfileirar(fila: FilaEmMemoria, ...coletas: AfericaoCriar[]) {
  for (const dados of coletas) {
    // criadoEm explícito e crescente: a ordem da fila é a ordem de coleta.
    await fila.adicionar({ ...novoItemDaFila(dados, 'LR-014'), criadoEm: dados.registrado_em })
  }
}

describe('SincronizadorDeFila sob quebra de rede', () => {
  let fila: FilaEmMemoria
  let servidor: ServidorFalso
  let sincronizador: SincronizadorDeFila

  beforeEach(() => {
    fila = new FilaEmMemoria()
    servidor = new ServidorFalso()
    sincronizador = new SincronizadorDeFila(fila, servidor)
  })

  it('envia tudo e esvazia a fila quando a rede está boa', async () => {
    await enfileirar(fila, coleta(), coleta(), coleta())

    const resultado = await sincronizador.sincronizar()

    expect(resultado).toEqual({ enviadas: 3, rejeitadas: 0, pendentes: 0, interrompidaPor: null })
    expect(await fila.listar()).toHaveLength(0)
    expect(servidor.gravadas.size).toBe(3)
  })

  it('para na queda de rede sem perder nenhuma coleta e retoma de onde parou', async () => {
    const [a, b, c] = [coleta(), coleta(), coleta()]
    await enfileirar(fila, a, b, c)
    servidor.roteiro = [null, 'antes_de_chegar']

    const primeira = await sincronizador.sincronizar()

    expect(primeira).toEqual({ enviadas: 1, rejeitadas: 0, pendentes: 2, interrompidaPor: 'rede' })
    expect((await fila.listar()).map((item) => item.idCliente)).toEqual([b.id_cliente, c.id_cliente])
    // Depois da queda o sincronizador não insiste nos itens seguintes.
    expect(servidor.chamadas).toBe(2)

    const segunda = await sincronizador.sincronizar()

    expect(segunda.enviadas).toBe(2)
    expect(await fila.listar()).toHaveLength(0)
    expect([...servidor.gravadas.keys()]).toEqual([a.id_cliente, b.id_cliente, c.id_cliente])
  })

  it('não duplica a coleta quando a resposta se perde depois de o servidor gravar', async () => {
    const dados = coleta()
    await enfileirar(fila, dados)
    servidor.roteiro = ['depois_de_gravar']

    const primeira = await sincronizador.sincronizar()
    expect(primeira.interrompidaPor).toBe('rede')
    // O item continua na fila: do ponto de vista do aparelho, o envio falhou.
    expect(await fila.listar()).toHaveLength(1)

    const segunda = await sincronizador.sincronizar()

    expect(segunda.enviadas).toBe(1)
    expect(await fila.listar()).toHaveLength(0)
    // Mesmo id_cliente nas duas tentativas: um único registro no servidor.
    expect(servidor.gravadas.size).toBe(1)
  })

  it('aguenta várias quedas seguidas até a rede estabilizar', async () => {
    await enfileirar(fila, coleta(), coleta())
    servidor.roteiro = ['antes_de_chegar', 'antes_de_chegar', 'depois_de_gravar']

    for (let rodada = 0; rodada < 5; rodada += 1) await sincronizador.sincronizar()

    expect(await fila.listar()).toHaveLength(0)
    expect(servidor.gravadas.size).toBe(2)
  })

  it('marca como rejeitada a coleta recusada pela trava de 24h e segue com as demais', async () => {
    const [antiga, boa] = [coleta(), coleta()]
    await enfileirar(fila, antiga, boa)
    servidor.rejeitarIds.add(antiga.id_cliente)

    const resultado = await sincronizador.sincronizar()

    expect(resultado).toEqual({ enviadas: 1, rejeitadas: 1, pendentes: 0, interrompidaPor: null })
    const [restante] = await fila.listar()
    expect(restante?.estado).toBe('rejeitada')
    expect(restante?.ultimoErro?.codigo).toBe('AfericaoForaDaJanela')

    // Rejeitada não volta a ser enviada sozinha: espera a decisão do operador.
    const chamadasAntes = servidor.chamadas
    await sincronizador.sincronizar()
    expect(servidor.chamadas).toBe(chamadasAntes)
  })

  it('interrompe com sessão expirada e mantém tudo pendente', async () => {
    await enfileirar(fila, coleta(), coleta())
    servidor.sessaoExpirada = true

    const resultado = await sincronizador.sincronizar()

    expect(resultado.interrompidaPor).toBe('sessao')
    expect((await fila.listar()).every((item) => item.estado === 'pendente')).toBe(true)
  })

  it('mantém pendente quando o servidor responde 5xx', async () => {
    await enfileirar(fila, coleta())
    const instavel: EnvioDeAfericao = {
      registrar: async () => {
        throw new ErroDeApi(503, 'ServicoIndisponivel', 'Banco fora do ar.')
      },
    }

    const resultado = await new SincronizadorDeFila(fila, instavel).sincronizar()

    expect(resultado.pendentes).toBe(1)
    const [item] = await fila.listar()
    expect(item?.estado).toBe('pendente')
    expect(item?.tentativas).toBe(1)
  })

  it('compartilha a rodada entre disparos simultâneos (online + Background Sync)', async () => {
    await enfileirar(fila, coleta(), coleta())

    const [r1, r2] = await Promise.all([sincronizador.sincronizar(), sincronizador.sincronizar()])

    expect(r1).toBe(r2)
    expect(servidor.chamadas).toBe(2)
  })
})
