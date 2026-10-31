/**
 * Background Sync (05/11).
 *
 * Pede ao navegador para acordar o Service Worker quando houver rede, mesmo com
 * o app fechado. Onde a API não existe (Safari/iOS, Firefox), a sincronização
 * continua acontecendo pela página: ao abrir o app, ao voltar a rede e em
 * intervalos enquanto houver fila.
 */

export const TAG_SINCRONIZACAO = 'sincronizar-afericoes'

interface RegistroComSync extends ServiceWorkerRegistration {
  sync?: { register(tag: string): Promise<void> }
}

export async function agendarSincronizacaoEmSegundoPlano(): Promise<boolean> {
  if (!('serviceWorker' in navigator)) return false
  try {
    const registro = (await navigator.serviceWorker.ready) as RegistroComSync
    if (!registro.sync) return false
    await registro.sync.register(TAG_SINCRONIZACAO)
    return true
  } catch {
    // Permissão negada ou SW ausente: a página assume a sincronização.
    return false
  }
}

/** O SW avisa a página aberta para ela mesma sincronizar (mesmo código das telas). */
export function aoPedidoDeSincronizacaoDoServiceWorker(acao: () => void): () => void {
  if (!('serviceWorker' in navigator)) return () => undefined
  const ouvinte = (evento: MessageEvent) => {
    if (evento.data?.tipo === 'sincronizar') acao()
  }
  navigator.serviceWorker.addEventListener('message', ouvinte)
  return () => navigator.serviceWorker.removeEventListener('message', ouvinte)
}
