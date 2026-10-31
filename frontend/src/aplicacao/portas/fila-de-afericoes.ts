/**
 * Porta da fila local de aferições (offline-first).
 *
 * Toda coleta que não chegou ao servidor fica aqui até ser enviada. O
 * `idCliente` é a chave e é o mesmo `id_cliente` mandado à API: reenviar um item
 * é seguro, o servidor reconhece a duplicata e devolve o registro existente.
 */

import type { AfericaoCriar } from '@/aplicacao/contratos/tipos'

export type EstadoDoItemDaFila = 'pendente' | 'rejeitada'

export interface ErroDoItemDaFila {
  codigo: string
  mensagem: string
  status: number | null
}

export interface ItemDaFila {
  idCliente: string
  dados: AfericaoCriar
  /** Código da leira no momento da coleta, para a tela funcionar sem rede. */
  rotuloDaLeira: string
  criadoEm: string
  estado: EstadoDoItemDaFila
  tentativas: number
  ultimoErro: ErroDoItemDaFila | null
}

export interface FilaDeAfericoes {
  adicionar(item: ItemDaFila): Promise<void>
  listar(): Promise<ItemDaFila[]>
  salvar(item: ItemDaFila): Promise<void>
  remover(idCliente: string): Promise<void>
}

export function novoItemDaFila(dados: AfericaoCriar, rotuloDaLeira: string): ItemDaFila {
  return {
    idCliente: dados.id_cliente,
    dados,
    rotuloDaLeira,
    criadoEm: new Date().toISOString(),
    estado: 'pendente',
    tentativas: 0,
    ultimoErro: null,
  }
}
