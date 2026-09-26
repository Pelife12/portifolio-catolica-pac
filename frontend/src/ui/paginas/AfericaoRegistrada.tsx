/**
 * Confirmação da coleta.
 *
 * Tela curta e inequívoca: o operador precisa saber, de relance e com o
 * termômetro na mão, que o dado foi aceito e o que vem depois. Também mostra o
 * que o motor de inferência (RF03) concluiu sobre a leira na volta do servidor.
 */

import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'

import type { Afericao } from '@/aplicacao/contratos/tipos'
import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import { formatarCoordenada, formatarDataHora } from '@/dominio/formatacao'
import { ROTULO_TIPO_ALERTA } from '@/dominio/rotulos'
import { classificarTemperatura, formatarTemperatura } from '@/dominio/temperatura'
import { Botao } from '@/ui/componentes/Botao'
import { Cartao } from '@/ui/componentes/Cartao'
import { Icone } from '@/ui/componentes/Icone'
import { Selo } from '@/ui/componentes/Selo'
import { CAMINHOS } from '@/ui/rotas/caminhos'

export function AfericaoRegistrada() {
  const { leiraId } = useParams<{ leiraId: string }>()
  const navegar = useNavigate()
  const { state } = useLocation()
  const afericao = (state as { afericao?: Afericao } | null)?.afericao ?? null

  const { data: alertas } = usarAlertas({ leiraId, status: 'aberto' })

  // Sem estado na navegação (recarregou a página), devolve para a lista.
  if (!afericao) {
    return (
      <section className="confirmacao">
        <p>Esta confirmação já foi encerrada.</p>
        <Link className="botao" to={CAMINHOS.leiras}>
          Voltar às leiras
        </Link>
      </section>
    )
  }

  const temperatura = Number(afericao.temperatura_celsius)
  const fase = classificarTemperatura(temperatura)

  return (
    <section className="pilha">
      <div className="confirmacao">
        <div className="confirmacao__marca" aria-hidden="true">
          <Icone nome="confirmado" tamanho={34} />
        </div>
        <h1>Aferição registrada</h1>
        <p className="confirmacao__valor">{formatarTemperatura(temperatura)} °C</p>
        <Selo tom={fase === 'termofilica' ? 'ok' : fase === 'excessiva' ? 'perigo' : 'atencao'}>
          {fase === 'termofilica'
            ? 'Fase termofílica mantida'
            : fase === 'excessiva'
              ? 'Calor excessivo'
              : 'Abaixo de 55 °C'}
        </Selo>
      </div>

      <Cartao compacto>
        <div className="pilha pilha--curta">
          <span className="rotulo">Trilha de auditoria</span>
          <p className="texto-secundario">
            Coleta em <strong>{formatarDataHora(afericao.registrado_em)}</strong>
          </p>
          <p className="texto-secundario">
            Local{' '}
            <span className="mono">
              {formatarCoordenada(afericao.latitude, afericao.longitude)}
            </span>
          </p>
          <p className="texto-secundario">
            Sincronizada em <strong>{formatarDataHora(afericao.sincronizado_em)}</strong>
          </p>
        </div>
      </Cartao>

      {alertas && alertas.length > 0 ? (
        <Cartao tom="atencao">
          <div className="pilha pilha--curta">
            <div className="linha">
              <Icone nome="alerta" cor="var(--atencao)" />
              <strong>
                {alertas.length === 1
                  ? '1 alerta aberto nesta leira'
                  : `${alertas.length} alertas abertos nesta leira`}
              </strong>
            </div>
            {alertas.slice(0, 3).map((alerta) => (
              <p key={alerta.id} className="texto-secundario">
                {ROTULO_TIPO_ALERTA[alerta.tipo]} · {alerta.mensagem}
              </p>
            ))}
            <Link className="botao botao--texto" to={CAMINHOS.alertas}>
              Ver central de alertas
            </Link>
          </div>
        </Cartao>
      ) : null}

      <div className="pilha pilha--curta">
        <Botao
          grande
          bloco
          onClick={() => navegar(CAMINHOS.novaAfericao(leiraId ?? ''), { replace: true })}
        >
          Nova coleta nesta leira
        </Botao>
        <Botao variante="secundario" bloco onClick={() => navegar(CAMINHOS.leiras)}>
          Voltar às leiras
        </Botao>
      </div>
    </section>
  )
}
