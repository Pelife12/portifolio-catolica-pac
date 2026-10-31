/**
 * Registro do Service Worker e troca de versão.
 *
 * Em desenvolvimento o SW fica desligado (cache atrapalha o HMR do Vite); para
 * testar o modo offline localmente, use `npm run build && npm run preview` ou
 * defina VITE_SW_EM_DESENVOLVIMENTO=true.
 */

type Ouvinte = (registro: ServiceWorkerRegistration) => void

const ouvintesDeNovaVersao = new Set<Ouvinte>()
let registroAtual: ServiceWorkerRegistration | null = null

export function swHabilitado(): boolean {
  return (
    'serviceWorker' in navigator &&
    (import.meta.env.PROD || import.meta.env.VITE_SW_EM_DESENVOLVIMENTO === 'true')
  )
}

export async function registrarServiceWorker(): Promise<void> {
  if (!swHabilitado()) return

  try {
    const registro = await navigator.serviceWorker.register('/sw.js', { scope: '/' })
    registroAtual = registro

    // Versão nova já baixada e esperando (a aba ficou aberta durante o deploy).
    if (registro.waiting && navigator.serviceWorker.controller) avisarNovaVersao(registro)

    registro.addEventListener('updatefound', () => {
      const instalando = registro.installing
      instalando?.addEventListener('statechange', () => {
        // Só é "atualização" se já havia um SW controlando a página.
        if (instalando.state === 'installed' && navigator.serviceWorker.controller) {
          avisarNovaVersao(registro)
        }
      })
    })

    // Quando a nova versão assume, recarrega uma única vez para usar o shell novo.
    let recarregando = false
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (recarregando) return
      recarregando = true
      window.location.reload()
    })
  } catch (erro) {
    // Sem SW o app continua funcionando online; só perde o modo offline.
    console.warn('Service Worker não registrado:', erro)
  }
}

function avisarNovaVersao(registro: ServiceWorkerRegistration): void {
  ouvintesDeNovaVersao.forEach((ouvinte) => ouvinte(registro))
}

export function aoSurgirNovaVersao(ouvinte: Ouvinte): () => void {
  ouvintesDeNovaVersao.add(ouvinte)
  if (registroAtual?.waiting && navigator.serviceWorker.controller) ouvinte(registroAtual)
  return () => ouvintesDeNovaVersao.delete(ouvinte)
}

/** Pede para a versão em espera assumir — chamado só quando o operador aceita. */
export function ativarNovaVersao(registro: ServiceWorkerRegistration): void {
  registro.waiting?.postMessage({ tipo: 'ativar-nova-versao' })
}

/** Mensagem genérica para o SW ativo (ex.: limpar o cache da API no logout). */
export function enviarAoServiceWorker(mensagem: { tipo: string }): void {
  if (!('serviceWorker' in navigator)) return
  navigator.serviceWorker.controller?.postMessage(mensagem)
}
