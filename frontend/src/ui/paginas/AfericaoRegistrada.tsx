/**
 * Confirmação da coleta.
 *
 * Tela curta e inequívoca: o operador precisa saber, de relance e com o
 * termômetro na mão, se o dado já está no servidor ou guardado no aparelho, e
 * o que vem depois. Quando a coleta subiu, mostra também o que o motor de
 * inferência (RF03) concluiu sobre a leira.
 */

import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'

import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import type { ResultadoDoRegistro } from '@/aplicacao/hooks/usar-afericoes'
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
  const resultado = (state as { resultado?: ResultadoDoRegistro } | null)?.resultado ?? null

  const { data: alertas } = usarAlertas({ leiraId, status: 'aberto' })

  // Sem estado na navegação (recarregou a página), devolve para a lista.
  if (!resultado) {
    return (
      <section className="confirmacao">
        <p>Esta confirmação já foi encerrada.</p>
        <Link className="botao" to={CAMINHOS.leiras}>
          Voltar às leiras
        </Link>
      </section>
    )
  }

  const naFila = resultado.tipo === 'na_fila'
  const registro =
    resultado.tipo === 'enviada'
      ? {
          temperatura: Number(resultado.afericao.temperatura_celsius),
          registradoEm: resultado.afericao.registrado_em,
          latitude: resultado.afericao.latitude,
          longitude: resultado.afericao.longitude,
          sincronizadoEm: resultado.afericao.sincronizado_em,
        }
      : {
          temperatura: resultado.item.dados.temperatura_celsius,
          registradoEm: resultado.item.dados.registrado_em,
          latitude: resultado.item.dados.latitude,
          longitude: resultado.item.dados.longitude,
          sincronizadoEm: null,
        }
  const fase = classificarTemperatura(registro.temperatura)

  return (
    <section className="pilha">
      <div className="confirmacao">
        <div
          className="confirmacao__marca"
          style={naFila ? { borderColor: 'var(--atencao)', color: 'var(--atencao)' } : undefined}
          aria-hidden="true"
        >
          <Icone nome={naFila ? 'recarregar' : 'confirmado'} tamanho={34} />
        </div>
        <h1>{naFila ? 'Salva no aparelho' : 'Aferição registrada'}</h1>
        <p className="confirmacao__valor">{formatarTemperatura(registro.temperatura)} °C</p>
        <Selo tom={fase === 'termofilica' ? 'ok' : fase === 'excessiva' ? 'perigo' : 'atencao'}>
          {fase === 'termofilica'
            ? 'Fase termofílica mantida'
            : fase === 'excessiva'
              ? 'Calor excessivo'
              : 'Abaixo de 55 °C'}
        </Selo>
        {naFila ? (
          <p className="texto-secundario" style={{ maxWidth: '34ch' }}>
            Sem conexão com o servidor. A coleta está na fila do aparelho e sobe quando a
            rede voltar.
          </p>
        ) : null}
      </div>

      <Cartao compacto>
        <div className="pilha pilha--curta">
          <span className="rotulo">Trilha de auditoria</span>
          <p className="texto-secundario">
            Coleta em <strong>{formatarDataHora(registro.registradoEm)}</strong>
          </p>
          <p className="texto-secundario">
            Local{' '}
            <span className="mono">{formatarCoordenada(registro.latitude, registro.longitude)}</span>
          </p>
          <p className="texto-secundario">
            {registro.sincronizadoEm ? (
              <>
                Sincronizada em <strong>{formatarDataHora(registro.sincronizadoEm)}</strong>
              </>
            ) : (
              <>
                Aguardando envio · <Link to={CAMINHOS.fila}>ver fila</Link>
              </>
            )}
          </p>
        </div>
      </Cartao>

      {!naFila && alertas && alertas.length > 0 ? (
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
