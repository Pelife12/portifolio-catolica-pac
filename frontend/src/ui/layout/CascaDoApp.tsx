/**
 * Casca das telas autenticadas: cabeçalho, aviso de rede e navegação.
 *
 * A navegação fica embaixo no celular (alcance do polegar) e migra para o topo
 * no desktop — a decisão é só de CSS, o HTML é o mesmo.
 */

import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import { usarSair, usarUsuarioAtual } from '@/aplicacao/hooks/usar-sessao'
import { ROTULO_PAPEL } from '@/dominio/rotulos'
import { AlternadorDeTema } from '@/ui/componentes/AlternadorDeTema'
import { Icone, type NomeDoIcone } from '@/ui/componentes/Icone'
import { usarStatusDeRede } from '@/ui/hooks/usar-status-de-rede'
import { CAMINHOS } from '@/ui/rotas/caminhos'

interface Aba {
  para: string
  texto: string
  icone: NomeDoIcone
}

const ABAS: Aba[] = [
  { para: CAMINHOS.leiras, texto: 'Leiras', icone: 'leira' },
  { para: CAMINHOS.painel, texto: 'Painel', icone: 'painel' },
  { para: CAMINHOS.alertas, texto: 'Alertas', icone: 'alertas' },
]

export function CascaDoApp() {
  const { data: usuario } = usarUsuarioAtual()
  const online = usarStatusDeRede()
  const sair = usarSair()
  const { pathname } = useLocation()

  // Marcador da aba: só alertas abertos entram, senão vira ruído permanente.
  const { data: alertasAbertos } = usarAlertas({ status: 'aberto' })
  const quantidadeDeAlertas = alertasAbertos?.length ?? 0

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

      <nav className="casca__navegacao" aria-label="Seções do aplicativo">
        {ABAS.map((aba) => (
          <NavLink
            key={aba.para}
            to={aba.para}
            className="casca__aba"
            // A aba de leiras segue ativa nas telas filhas (histórico, coleta).
            aria-current={pathname.startsWith(aba.para) ? 'page' : undefined}
          >
            <span style={{ position: 'relative' }}>
              <Icone nome={aba.icone} tamanho={20} />
              {aba.para === CAMINHOS.alertas && quantidadeDeAlertas > 0 ? (
                <span className="casca__aba__marcador">{quantidadeDeAlertas}</span>
              ) : null}
            </span>
            {aba.texto}
          </NavLink>
        ))}
      </nav>

      <main className="casca__conteudo">
        <Outlet />
      </main>
    </div>
  )
}
