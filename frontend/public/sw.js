/*
 * Service Worker do Aferra.
 *
 * Escrito à mão, sem Workbox: as estratégias são poucas e precisam ser lidas e
 * defendidas na banca. Três responsabilidades:
 *
 * 1. App shell (22/10): o app abre sem conexão depois da primeira visita.
 *    - navegação: rede primeiro, cai para o index.html em cache;
 *    - /assets/* (nomes com hash do Vite, imutáveis): cache primeiro;
 *    - fontes do Google: stale-while-revalidate.
 * 2. Leitura offline (29/10): GET na API usa rede primeiro e, sem rede, devolve
 *    a última resposta guardada — a leira continua consultável no pátio.
 * 3. Background Sync (05/11): ao voltar a rede, envia a fila de aferições do
 *    IndexedDB mesmo com o app fechado.
 *
 * O esquema do IndexedDB (nome, versão e stores) é o mesmo de
 * src/infraestrutura/armazenamento/banco-local.ts — os dois mudam juntos.
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

const TAG_SINCRONIZACAO = 'sincronizar-afericoes'

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

// ---------------------------------------------------------------------------
// Background Sync (05/11)
// ---------------------------------------------------------------------------

self.addEventListener('sync', (evento) => {
  if (evento.tag === TAG_SINCRONIZACAO) evento.waitUntil(sincronizar())
})

async function sincronizar() {
  // Com o app aberto, quem envia é a página (mesmo código das telas e dos
  // testes); o SW só avisa. Com o app fechado, o próprio SW esvazia a fila.
  const janelas = await self.clients.matchAll({ type: 'window' })
  if (janelas.length > 0) {
    janelas.forEach((janela) => janela.postMessage({ tipo: 'sincronizar' }))
    return
  }
  await esvaziarFila()
}

const BANCO = 'aferra'
const VERSAO_DO_BANCO = 1
const STORE_FILA = 'fila_afericoes'
const STORE_CREDENCIAL = 'credencial'

function abrirBanco() {
  return new Promise((resolver, rejeitar) => {
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
    pedido.onerror = () => rejeitar(pedido.error)
  })
}

function operar(banco, store, modo, acao) {
  return new Promise((resolver, rejeitar) => {
    const transacao = banco.transaction(store, modo)
    const pedido = acao(transacao.objectStore(store))
    transacao.oncomplete = () => resolver(pedido && pedido.result)
    transacao.onerror = () => rejeitar(transacao.error)
  })
}

async function esvaziarFila() {
  const banco = await abrirBanco()
  const credencial = await operar(banco, STORE_CREDENCIAL, 'readonly', (s) => s.get('sessao'))
  // Sem sessão válida não há como autenticar: a fila espera o próximo login.
  if (!credencial || credencial.expiraEm <= Date.now()) return

  const itens = await operar(banco, STORE_FILA, 'readonly', (s) => s.getAll())
  for (const item of itens) {
    if (item.estado !== 'pendente') continue

    let resposta
    try {
      resposta = await fetch(`${credencial.urlBase}/afericoes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          Authorization: `Bearer ${credencial.token}`,
        },
        body: JSON.stringify(item.dados),
      })
    } catch (erro) {
      // Rede caiu de novo: rejeitar a promessa faz o navegador reagendar o sync.
      throw erro
    }

    if (resposta.ok) {
      // 201 (criada) ou 200 (id_cliente já existia): nos dois casos está no servidor.
      await operar(banco, STORE_FILA, 'readwrite', (s) => s.delete(item.idCliente))
    } else if (resposta.status === 401) {
      return
    } else if (resposta.status >= 400 && resposta.status < 500) {
      // Recusa de negócio (trava de 24h, leira removida...): repetir não resolve.
      let mensagem = `Recusada pelo servidor (HTTP ${resposta.status}).`
      let codigo = `HTTP_${resposta.status}`
      try {
        const corpo = await resposta.json()
        if (corpo.mensagem) mensagem = corpo.mensagem
        if (corpo.erro) codigo = corpo.erro
      } catch {
        // corpo sem JSON
      }
      await operar(banco, STORE_FILA, 'readwrite', (s) =>
        s.put({
          ...item,
          estado: 'rejeitada',
          tentativas: item.tentativas + 1,
          ultimoErro: { codigo, mensagem, status: resposta.status },
        }),
      )
    } else {
      throw new Error(`Servidor indisponível (HTTP ${resposta.status}).`)
    }
  }
}
