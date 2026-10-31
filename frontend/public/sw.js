/*
 * Service Worker do Aferra.
 *
 * Escrito à mão, sem Workbox: as estratégias são poucas e precisam ser lidas e
 * defendidas na banca. Duas responsabilidades:
 *
 * 1. App shell (22/10): o app abre sem conexão depois da primeira visita.
 *    - navegação: rede primeiro, cai para o index.html em cache;
 *    - /assets/* (nomes com hash do Vite, imutáveis): cache primeiro;
 *    - fontes do Google: stale-while-revalidate.
 * 2. Leitura offline (29/10): GET na API usa rede primeiro e, sem rede, devolve
 *    a última resposta guardada — a leira continua consultável no pátio.
 */

const VERSAO = 'v1'
const CACHE_SHELL = `aferra-shell-${VERSAO}`
const CACHE_ASSETS = `aferra-assets-${VERSAO}`
const CACHE_API = `aferra-api-${VERSAO}`
const CACHE_FONTES = `aferra-fontes-${VERSAO}`
const CACHES_ATUAIS = [CACHE_SHELL, CACHE_ASSETS, CACHE_API, CACHE_FONTES]

const SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/icones/icone-192.png',
  '/icones/icone-512.png',
]

// ---------------------------------------------------------------------------
// Ciclo de vida
// ---------------------------------------------------------------------------

self.addEventListener('install', (evento) => {
  evento.waitUntil(caches.open(CACHE_SHELL).then((cache) => cache.addAll(SHELL)))
  // Sem skipWaiting automático: a página pergunta antes de trocar de versão,
  // para não recarregar a tela no meio de uma coleta.
})

self.addEventListener('activate', (evento) => {
  evento.waitUntil(
    (async () => {
      const nomes = await caches.keys()
      await Promise.all(
        nomes
          .filter((nome) => nome.startsWith('aferra-') && !CACHES_ATUAIS.includes(nome))
          .map((nome) => caches.delete(nome)),
      )
      await self.clients.claim()
    })(),
  )
})

self.addEventListener('message', (evento) => {
  const tipo = evento.data && evento.data.tipo
  if (tipo === 'ativar-nova-versao') self.skipWaiting()
  // No logout os dados da usina não podem ficar no aparelho para o próximo usuário.
  if (tipo === 'limpar-cache-api') evento.waitUntil(caches.delete(CACHE_API))
})

// ---------------------------------------------------------------------------
// Estratégias de cache
// ---------------------------------------------------------------------------

self.addEventListener('fetch', (evento) => {
  const { request } = evento
  const url = new URL(request.url)

  if (request.method !== 'GET') return

  if (request.mode === 'navigate') {
    evento.respondWith(navegacao(request))
    return
  }

  if (url.pathname.includes('/api/v1/')) {
    // O laudo é gerado na hora e não faz sentido servi-lo velho.
    if (url.pathname.endsWith('/laudo')) return
    evento.respondWith(redePrimeiro(request, CACHE_API))
    return
  }

  if (url.origin === self.location.origin && url.pathname.startsWith('/assets/')) {
    evento.respondWith(cachePrimeiro(request, CACHE_ASSETS))
    return
  }

  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    evento.respondWith(revalidarEmSegundoPlano(request, CACHE_FONTES))
  }
})

async function navegacao(request) {
  try {
    const resposta = await fetch(request)
    const cache = await caches.open(CACHE_SHELL)
    cache.put('/index.html', resposta.clone())
    return resposta
  } catch {
    // SPA: qualquer rota abre o mesmo index.html; o React Router resolve o resto.
    const emCache = await caches.match('/index.html')
    return emCache || Response.error()
  }
}

async function cachePrimeiro(request, nomeDoCache) {
  const emCache = await caches.match(request)
  if (emCache) return emCache
  const resposta = await fetch(request)
  if (resposta.ok) (await caches.open(nomeDoCache)).put(request, resposta.clone())
  return resposta
}

async function redePrimeiro(request, nomeDoCache) {
  const cache = await caches.open(nomeDoCache)
  try {
    const resposta = await fetch(request)
    if (resposta.ok) cache.put(request, resposta.clone())
    return resposta
  } catch {
    const emCache = await cache.match(request)
    if (emCache) {
      // Marca a resposta como vinda do cache para a tela poder avisar o operador.
      const cabecalhos = new Headers(emCache.headers)
      cabecalhos.set('X-Aferra-Offline', '1')
      return new Response(await emCache.blob(), {
        status: emCache.status,
        statusText: emCache.statusText,
        headers: cabecalhos,
      })
    }
    return Response.error()
  }
}

async function revalidarEmSegundoPlano(request, nomeDoCache) {
  const cache = await caches.open(nomeDoCache)
  const emCache = await cache.match(request)
  const atualizacao = fetch(request)
    .then((resposta) => {
      if (resposta.ok || resposta.type === 'opaque') cache.put(request, resposta.clone())
      return resposta
    })
    .catch(() => emCache)
  return emCache || atualizacao
}

