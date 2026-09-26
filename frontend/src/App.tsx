/** Composição dos provedores da aplicação. */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { useState } from 'react'

import { ProvedorDeDependencias, type Dependencias } from '@/aplicacao/dependencias'
import { ErroDeApi } from '@/infraestrutura/http/erros'
import { ProvedorDeTema } from '@/ui/hooks/usar-tema'
import { Rotas } from '@/ui/rotas/rotas'

function criarQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Erro de negócio (4xx) não melhora com repetição; falha de rede, sim.
        retry: (tentativas, erro) => !(erro instanceof ErroDeApi) && tentativas < 2,
        staleTime: 30_000,
        refetchOnWindowFocus: true,
      },
      mutations: { retry: false },
    },
  })
}

export function App({ dependencias }: { dependencias?: Dependencias }) {
  const [cliente] = useState(criarQueryClient)

  return (
    <QueryClientProvider client={cliente}>
      <ProvedorDeDependencias dependencias={dependencias}>
        <ProvedorDeTema>
          <BrowserRouter>
            <Rotas />
          </BrowserRouter>
        </ProvedorDeTema>
      </ProvedorDeDependencias>
    </QueryClientProvider>
  )
}
