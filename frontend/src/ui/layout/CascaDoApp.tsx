/**
 * Casca das telas autenticadas: cabeçalho, aviso de rede e conteúdo.
 *
 * A navegação entre seções entra junto com o painel e os alertas (15/10); nesta
 * entrega o app tem uma única seção, a lista de leiras.
 */

import { Outlet } from 'react-router-dom'

import { usarSair, usarUsuarioAtual } from '@/aplicacao/hooks/usar-sessao'
import { AlternadorDeTema } from '@/ui/componentes/AlternadorDeTema'
import { Icone } from '@/ui/componentes/Icone'
import { ROTULO_PAPEL } from '@/dominio/rotulos'
import { usarStatusDeRede } from '@/ui/hooks/usar-status-de-rede'

export function CascaDoApp() {
  const { data: usuario } = usarUsuarioAtual()
  const online = usarStatusDeRede()
  const sair = usarSair()

  return (
    <div className="casca">
      <header className="casca__topo">
        <div className="casca__identidade">
          <div className="casca__marca" aria-hidden="true">
            A
          </div>
          <div className="casca__titulo">
            <h1>Aferra</h1>
            <p className="casca__subtitulo">
              {usuario ? `${usuario.nome} · ${ROTULO_PAPEL[usuario.papel]}` : 'Carregando sessão…'}
            </p>
          </div>
        </div>
        <AlternadorDeTema />
        <button
          type="button"
          className="botao botao--secundario"
          style={{ width: 44, minHeight: 44, padding: 0, borderRadius: 'var(--raio-interno)' }}
          onClick={sair}
          aria-label="Sair da conta"
          title="Sair"
        >
          <Icone nome="sair" tamanho={18} />
        </button>
      </header>

      {!online ? (
        <p className="faixa-offline" role="status">
          <Icone nome="alerta" tamanho={14} />
          Sem conexão · as coletas ficam salvas no aparelho
        </p>
      ) : null}

      <main className="casca__conteudo">
        <Outlet />
      </main>
    </div>
  )
}
