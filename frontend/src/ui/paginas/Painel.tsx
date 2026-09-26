/**
 * Painel de gestão: como está o pátio agora.
 *
 * Responde a três perguntas do gestor, na ordem em que ele as faz: alguma leira
 * saiu da faixa? alguma leira ficou sem coleta? o ciclo está cumprindo a regra
 * dos 55 °C? Os números vêm do histórico já sincronizado — a autoridade sobre
 * alertas continua sendo do motor no servidor.
 */

import { Link } from 'react-router-dom'

import type { Afericao, Leira } from '@/aplicacao/contratos/tipos'
import { usarAfericoes } from '@/aplicacao/hooks/usar-afericoes'
import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import { usarLeiras } from '@/aplicacao/hooks/usar-leiras'
import { resumirCiclo, type ResumoDoCiclo } from '@/dominio/ciclo'
import { JANELA_RETROATIVA_HORAS } from '@/dominio/faixas'
import { diasDesde, formatarNumero } from '@/dominio/formatacao'
import { ROTULO_STATUS_LEIRA } from '@/dominio/rotulos'
import { formatarTemperatura } from '@/dominio/temperatura'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Cartao } from '@/ui/componentes/Cartao'
import { ListaEsqueleto } from '@/ui/componentes/Carregando'
import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Selo } from '@/ui/componentes/Selo'
import { CAMINHOS } from '@/ui/rotas/caminhos'

/** Leira encerrada não conta para o acompanhamento do pátio. */
const STATUS_EM_ACOMPANHAMENTO: Leira['status'][] = ['em_montagem', 'ativa', 'em_maturacao']

export function Painel() {
  const leiras = usarLeiras()
  const afericoes = usarAfericoes()
  const alertasAbertos = usarAlertas({ status: 'aberto' })

  const emAcompanhamento = (leiras.data ?? []).filter((leira) =>
    STATUS_EM_ACOMPANHAMENTO.includes(leira.status),
  )

  const resumoPorLeira = new Map<string, ResumoDoCiclo>()
  for (const leira of emAcompanhamento) {
    const doLeira = (afericoes.data ?? []).filter(
      (afericao: Afericao) => afericao.leira_id === leira.id,
    )
    resumoPorLeira.set(
      leira.id,
      resumirCiclo(
        doLeira.map((afericao) => ({
          temperatura: Number(afericao.temperatura_celsius),
          registradoEm: new Date(afericao.registrado_em),
        })),
        new Date(leira.data_montagem),
      ),
    )
  }

  const semColetaRecente = emAcompanhamento.filter((leira) => {
    const resumo = resumoPorLeira.get(leira.id)
    return resumo?.horasSemColeta === null || (resumo?.horasSemColeta ?? 0) > JANELA_RETROATIVA_HORAS
  })

  const foraDaFaixa = emAcompanhamento.filter((leira) => {
    const resumo = resumoPorLeira.get(leira.id)
    return resumo?.prazoTermofilicoVencido || resumo?.quedaBrusca
  })

  const coletasDeHoje = (afericoes.data ?? []).filter(
    (afericao) => new Date(afericao.registrado_em).toDateString() === new Date().toDateString(),
  )

  const carregando = leiras.isPending || afericoes.isPending

  return (
    <section>
      <div className="pagina__cabecalho">
        <div>
          <h1>Painel de gestão</h1>
          <p className="texto-secundario">Situação do pátio agora</p>
        </div>
      </div>

      {leiras.isError ? (
        <FaixaDeErro
          titulo="Não foi possível carregar o painel"
          acoes={[{ texto: 'Tentar novamente', ao: () => void leiras.refetch() }]}
        >
          {descreverErro(leiras.error)}
        </FaixaDeErro>
      ) : null}

      <div className="pilha">
        <Cartao>
          <div className="indicadores">
            <div>
              <p className="indicador__rotulo">Leiras ativas</p>
              <p className="indicador__valor">{emAcompanhamento.length}</p>
              <p className="indicador__nota">de {leiras.data?.length ?? 0} cadastradas</p>
            </div>
            <div>
              <p className="indicador__rotulo">Coletas hoje</p>
              <p className="indicador__valor">{coletasDeHoje.length}</p>
              <p className="indicador__nota">aferições sincronizadas</p>
            </div>
            <div>
              <p className="indicador__rotulo">Sem coleta em 24 h</p>
              <p
                className={`indicador__valor ${
                  semColetaRecente.length > 0 ? 'indicador__valor--atencao' : 'indicador__valor--ok'
                }`}
              >
                {semColetaRecente.length}
              </p>
              <p className="indicador__nota">leiras a visitar</p>
            </div>
            <div>
              <p className="indicador__rotulo">Alertas abertos</p>
              <p
                className={`indicador__valor ${
                  (alertasAbertos.data?.length ?? 0) > 0
                    ? 'indicador__valor--perigo'
                    : 'indicador__valor--ok'
                }`}
              >
                {alertasAbertos.data?.length ?? 0}
              </p>
              <p className="indicador__nota">
                <Link to={CAMINHOS.alertas}>ver a central</Link>
              </p>
            </div>
          </div>
        </Cartao>

        {foraDaFaixa.length > 0 ? (
          <Cartao tom="critico">
            <span className="rotulo">Exigem atenção</span>
            <div className="pilha pilha--curta" style={{ marginTop: 'var(--esp-3)' }}>
              {foraDaFaixa.map((leira) => {
                const resumo = resumoPorLeira.get(leira.id)
                return (
                  <p key={leira.id} className="texto-secundario">
                    <Link to={CAMINHOS.leira(leira.id)}>
                      <strong>{leira.codigo}</strong>
                    </Link>{' '}
                    ·{' '}
                    {resumo?.prazoTermofilicoVencido
                      ? 'não atingiu 55 °C dentro de 72 h'
                      : 'queda brusca de temperatura no histórico'}
                  </p>
                )
              })}
            </div>
          </Cartao>
        ) : null}

        <Cartao>
          <span className="rotulo">Leiras em acompanhamento</span>
          <div style={{ marginTop: 'var(--esp-3)' }}>
            {carregando ? <ListaEsqueleto itens={4} altura={40} /> : null}

            {!carregando && emAcompanhamento.length === 0 ? (
              <EstadoVazio
                titulo="Nenhuma leira em acompanhamento"
                acao={
                  <Link className="botao" to={CAMINHOS.novaLeira}>
                    Cadastrar leira
                  </Link>
                }
              >
                Cadastre uma leira para o painel começar a acompanhar o ciclo.
              </EstadoVazio>
            ) : null}

            {emAcompanhamento.length > 0 ? (
              <div className="tabela-envolvente">
                <table className="tabela">
                  <thead>
                    <tr>
                      <th>Leira</th>
                      <th>Status</th>
                      <th>Dia</th>
                      <th>Última leitura</th>
                      <th>Pico</th>
                      <th>Ciclo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {emAcompanhamento.map((leira) => {
                      const resumo = resumoPorLeira.get(leira.id)
                      const ultimaLeitura = resumo?.ultimaLeitura ?? null
                      const pico = resumo?.pico ?? null
                      return (
                        <tr key={leira.id}>
                          <td>
                            <Link to={CAMINHOS.leira(leira.id)}>{leira.codigo}</Link>
                          </td>
                          <td>{ROTULO_STATUS_LEIRA[leira.status]}</td>
                          <td className="numero">{diasDesde(leira.data_montagem)}</td>
                          <td className="numero">
                            {ultimaLeitura
                              ? `${formatarTemperatura(ultimaLeitura.temperatura)} °C · há ${formatarNumero(
                                  resumo?.horasSemColeta ?? 0,
                                  0,
                                )} h`
                              : 'sem coleta'}
                          </td>
                          <td className="numero">
                            {pico !== null ? `${formatarTemperatura(pico)} °C` : '—'}
                          </td>
                          <td>
                            {resumo?.termofilicaNoPrazo ? (
                              <Selo tom="ok">conforme</Selo>
                            ) : resumo?.prazoTermofilicoVencido ? (
                              <Selo tom="perigo">fora da regra</Selo>
                            ) : (
                              <Selo tom="atencao">em aquecimento</Selo>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        </Cartao>
      </div>
    </section>
  )
}
