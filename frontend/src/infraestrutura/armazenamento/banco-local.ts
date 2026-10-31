/**
 * Acesso ao IndexedDB do Aferra.
 *
 * O mesmo banco é aberto pelo Service Worker (public/sw.js) para esvaziar a
 * fila com o app fechado: nome, versão e stores precisam mudar nos dois lugares.
 */

export const BANCO = 'aferra'
export const VERSAO_DO_BANCO = 1
export const STORE_FILA = 'fila_afericoes'
export const STORE_CREDENCIAL = 'credencial'

let conexao: Promise<IDBDatabase> | null = null

export function indexedDbDisponivel(): boolean {
  try {
    return typeof indexedDB !== 'undefined'
  } catch {
    return false
  }
}

export function abrirBanco(): Promise<IDBDatabase> {
  conexao ??= new Promise<IDBDatabase>((resolver, rejeitar) => {
    const pedido = indexedDB.open(BANCO, VERSAO_DO_BANCO)
    pedido.onupgradeneeded = () => {
      const banco = pedido.result
      if (!banco.objectStoreNames.contains(STORE_FILA)) {
        banco.createObjectStore(STORE_FILA, { keyPath: 'idCliente' })
      }
      if (!banco.objectStoreNames.contains(STORE_CREDENCIAL)) {
        banco.createObjectStore(STORE_CREDENCIAL)
      }
    }
    pedido.onsuccess = () => resolver(pedido.result)
    pedido.onerror = () => {
      conexao = null
      rejeitar(pedido.error)
    }
  })
  return conexao
}

/** Executa uma operação numa transação e resolve quando ela é confirmada. */
export async function operar<T>(
  store: string,
  modo: IDBTransactionMode,
  acao: (objectStore: IDBObjectStore) => IDBRequest<T> | void,
): Promise<T | undefined> {
  const banco = await abrirBanco()
  return new Promise<T | undefined>((resolver, rejeitar) => {
    const transacao = banco.transaction(store, modo)
    const pedido = acao(transacao.objectStore(store))
    // Resolve no oncomplete, não no onsuccess do pedido: só aí o dado está gravado.
    transacao.oncomplete = () => resolver(pedido ? pedido.result : undefined)
    transacao.onerror = () => rejeitar(transacao.error)
    transacao.onabort = () => rejeitar(transacao.error)
  })
}
