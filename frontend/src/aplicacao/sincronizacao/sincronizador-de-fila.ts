/**
 * Envio da fila local de aferições para a API.
 *
 * Regras:
 * - envia na ordem de coleta, um item por vez (o motor do servidor avalia a
 *   leira a cada coleta nova, e a ordem importa para a detecção de queda);
 * - sucesso (201 criada ou 200 já existente) tira o item da fila;
 * - falha de rede interrompe a rodada: os itens seguintes também falhariam;
 * - 401 interrompe: sem sessão, nada passa até o próximo login;
 * - outro 4xx (trava de 24h, por exemplo) marca o item como rejeitado: repetir
 *   não muda a resposta, então ele sai das rodadas e espera o operador;
 * - duas chamadas simultâneas compartilham a mesma rodada, para o mesmo item
 *   não ser enviado em paralelo.
 */

import type { Afericao, AfericaoCriar } from '@/aplicacao/contratos/tipos'
import type { FilaDeAfericoes, ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'
import { ErroDeApi, ErroDeRede } from '@/infraestrutura/http/erros'

export interface EnvioDeAfericao {
  registrar(dados: AfericaoCriar): Promise<Afericao>
}

export interface ResultadoDaSincronizacao {
  enviadas: number
  rejeitadas: number
  pendentes: number
  interrompidaPor: 'rede' | 'sessao' | null
}

export class SincronizadorDeFila {
  private rodadaAtual: Promise<ResultadoDaSincronizacao> | null = null

  constructor(
    private readonly fila: FilaDeAfericoes,
    private readonly envio: EnvioDeAfericao,
  ) {}

  sincronizar(): Promise<ResultadoDaSincronizacao> {
    this.rodadaAtual ??= this.executarRodada().finally(() => {
      this.rodadaAtual = null
    })
    return this.rodadaAtual
  }

  private async executarRodada(): Promise<ResultadoDaSincronizacao> {
    const resultado: ResultadoDaSincronizacao = {
      enviadas: 0,
      rejeitadas: 0,
      pendentes: 0,
      interrompidaPor: null,
    }

    const pendentes = (await this.fila.listar()).filter((item) => item.estado === 'pendente')

    for (const item of pendentes) {
      if (resultado.interrompidaPor) {
        resultado.pendentes += 1
        continue
      }

      try {
        await this.envio.registrar(item.dados)
        await this.fila.remover(item.idCliente)
        resultado.enviadas += 1
      } catch (erro) {
        if (erro instanceof ErroDeRede) {
          resultado.pendentes += 1
          resultado.interrompidaPor = 'rede'
        } else if (erro instanceof ErroDeApi && erro.naoAutenticado) {
          resultado.pendentes += 1
          resultado.interrompidaPor = 'sessao'
        } else if (erro instanceof ErroDeApi && erro.status >= 400 && erro.status < 500) {
          // Recusa de negócio (trava de 24h, leira removida, validação): reenviar
          // não muda a resposta. O item sai da rodada e espera o operador decidir.
          await this.fila.salvar({ ...registrarFalha(item, erro), estado: 'rejeitada' })
          resultado.rejeitadas += 1
        } else {
          // 5xx ou erro inesperado: o servidor pode se recuperar, fica pendente.
          await this.fila.salvar(registrarFalha(item, erro))
          resultado.pendentes += 1
        }
      }
    }

    return resultado
  }
}

function registrarFalha(item: ItemDaFila, erro: unknown): ItemDaFila {
  return {
    ...item,
    tentativas: item.tentativas + 1,
    ultimoErro:
      erro instanceof ErroDeApi
        ? { codigo: erro.codigo, mensagem: erro.message, status: erro.status }
        : { codigo: 'desconhecido', mensagem: String(erro), status: null },
  }
}
