/**
 * Casca das telas autenticadas: cabeçalho, aviso de rede e navegação.
 *
 * A navegação fica embaixo no celular (alcance do polegar) e migra para o topo
 * no desktop — a decisão é só de CSS, o HTML é o mesmo.
 */

import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import { usarFila, usarSincronizacaoAutomatica } from '@/aplicacao/hooks/usar-fila'
import { usarSair, usarUsuarioAtual } from '@/aplicacao/hooks/usar-sessao'
import { ROTULO_PAPEL } from '@/dominio/rotulos'
import { AlternadorDeTema } from '@/ui/componentes/AlternadorDeTema'
import { AvisoDeNovaVersao } from '@/ui/componentes/AvisoDeNovaVersao'
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
  { para: CAMINHOS.fila, texto: 'Fila', icone: 'recarregar' },
]

export function CascaDoApp() {
  const { data: usuario } = usarUsuarioAtual()
  const online = usarStatusDeRede()
  const sair = usarSair()
  const { pathname } = useLocation()

  // Marcador da aba: só alertas abertos entram, senão vira ruído permanente.
  const { data: alertasAbertos } = usarAlertas({ status: 'aberto' })
  // Indicador de sincronização (29/10): coletas que ainda estão só no aparelho.
  const { data: fila } = usarFila()
  usarSincronizacaoAutomatica()
  const marcadores: Record<string, number> = {
    [CAMINHOS.alertas]: alertasAbertos?.length ?? 0,
    // Pendentes e recusadas: as duas pedem atenção do operador.
    [CAMINHOS.fila]: fila?.length ?? 0,
  }

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

      <AvisoDeNovaVersao />

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
              {(marcadores[aba.para] ?? 0) > 0 ? (
                <span
                  className={`casca__aba__marcador${
                    aba.para === CAMINHOS.fila ? ' casca__aba__marcador--atencao' : ''
                  }`}
                >
                  {marcadores[aba.para]}
                </span>
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
