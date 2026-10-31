/**
 * Fila em memória: usada nos testes e como reserva quando o navegador não
 * oferece IndexedDB (modo privado antigo). Nesse caso a fila vale só enquanto a
 * aba estiver aberta — melhor que perder a coleta na hora.
 */

import type { FilaDeAfericoes, ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'

export class FilaEmMemoria implements FilaDeAfericoes {
  private readonly itens = new Map<string, ItemDaFila>()

  async adicionar(item: ItemDaFila): Promise<void> {
    this.itens.set(item.idCliente, structuredClone(item))
  }

  async listar(): Promise<ItemDaFila[]> {
    return [...this.itens.values()]
      .map((item) => structuredClone(item))
      .sort((a, b) => a.criadoEm.localeCompare(b.criadoEm))
  }

  async salvar(item: ItemDaFila): Promise<void> {
    this.itens.set(item.idCliente, structuredClone(item))
  }

  async remover(idCliente: string): Promise<void> {
    this.itens.delete(idCliente)
  }
}
