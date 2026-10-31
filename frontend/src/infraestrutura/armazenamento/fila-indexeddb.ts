/** Fila de aferições persistida no IndexedDB do aparelho. */

import type { FilaDeAfericoes, ItemDaFila } from '@/aplicacao/portas/fila-de-afericoes'

import { operar, STORE_FILA } from './banco-local'

export class FilaIndexedDb implements FilaDeAfericoes {
  async adicionar(item: ItemDaFila): Promise<void> {
    // put, e não add: reenfileirar o mesmo id_cliente substitui, não duplica.
    await operar(STORE_FILA, 'readwrite', (store) => store.put(item))
  }

  async listar(): Promise<ItemDaFila[]> {
    const itens = (await operar<ItemDaFila[]>(STORE_FILA, 'readonly', (store) => store.getAll())) ?? []
    // Mais antigas primeiro: a ordem de envio respeita a ordem de coleta.
    return itens.sort((a, b) => a.criadoEm.localeCompare(b.criadoEm))
  }

  async salvar(item: ItemDaFila): Promise<void> {
    await operar(STORE_FILA, 'readwrite', (store) => store.put(item))
  }

  async remover(idCliente: string): Promise<void> {
    await operar(STORE_FILA, 'readwrite', (store) => store.delete(idCliente))
  }
}
