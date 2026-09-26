/** Histórico de medições de uma leira: curva, indicadores do ciclo e tabela. */

import { Link, useNavigate, useParams } from 'react-router-dom'

import { usarAfericoes } from '@/aplicacao/hooks/usar-afericoes'
import { usarAlertas } from '@/aplicacao/hooks/usar-alertas'
import { usarLeira } from '@/aplicacao/hooks/usar-leiras'
import { resumirCiclo } from '@/dominio/ciclo'
import { TEMPERATURA_TERMOFILICA_MINIMA } from '@/dominio/faixas'
import {
  diasDesde,
  formatarCoordenada,
  formatarDataHora,
  formatarMassa,
  formatarNumero,
} from '@/dominio/formatacao'
import { ROTULO_STATUS_LEIRA, ROTULO_TIPO_ALERTA } from '@/dominio/rotulos'
import { formatarTemperatura } from '@/dominio/temperatura'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Cartao } from '@/ui/componentes/Cartao'
import { Esqueleto, ListaEsqueleto } from '@/ui/componentes/Carregando'
import { EstadoVazio } from '@/ui/componentes/EstadoVazio'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { GraficoDeTemperatura } from '@/ui/componentes/GraficoDeTemperatura'
import { Icone } from '@/ui/componentes/Icone'
import { Selo } from '@/ui/componentes/Selo'
import { CAMINHOS } from '@/ui/rotas/caminhos'

export function HistoricoDaLeira() {
  const { leiraId } = useParams<{ leiraId: string }>()
  const navegar = useNavigate()

  const leira = usarLeira(leiraId)
  const afericoes = usarAfericoes(leiraId)
  const alertas = usarAlertas({ leiraId })

  const resumo =
    leira.data && afericoes.data
      ? resumirCiclo(
          afericoes.data.map((afericao) => ({
            temperatura: Number(afericao.temperatura_celsius),
            registradoEm: new Date(afericao.registrado_em),
          })),
          new Date(leira.data.data_montagem),
        )
      : null

  // Extraídos antes do JSX: evita encadear verificações de nulo no meio da tela.
  const ultimaLeitura = resumo?.ultimaLeitura ?? null
  const pico = resumo?.pico ?? null
  const horasSemColeta = resumo?.horasSemColeta ?? null

  return (
    <section>
      <button type="button" className="pagina__voltar" onClick={() => navegar(CAMINHOS.leiras)}>
        <Icone nome="seta-esquerda" tamanho={16} />
        Leiras
      </button>

      <div className="pagina__cabecalho">
        <div>
          <h1>{leira.data ? leira.data.codigo : 'Leira'}</h1>
          <p className="casca__subtitulo">
            {leira.data
              ? `${ROTULO_STATUS_LEIRA[leira.data.status]} · dia ${diasDesde(
                  leira.data.data_montagem,
                )} do ciclo`
              : 'Carregando…'}
          </p>
        </div>
        {leira.data && leira.data.status !== 'encerrada' ? (
          <Link className="botao" to={CAMINHOS.novaAfericao(leira.data.id)}>
            Aferir
          </Link>
        ) : null}
      </div>

      {leira.isError ? (
        <FaixaDeErro
          titulo="Não foi possível carregar a leira"
          acoes={[{ texto: 'Tentar novamente', ao: () => void leira.refetch() }]}
        >
          {descreverErro(leira.error)}
        </FaixaDeErro>
      ) : null}

      <div className="pilha">
        {leira.data ? (
          <Cartao>
            <div className="indicadores">
              <div>
                <p className="indicador__rotulo">Última leitura</p>
                <p
                  className={`indicador__valor ${
                    ultimaLeitura && ultimaLeitura.temperatura >= TEMPERATURA_TERMOFILICA_MINIMA
                      ? 'indicador__valor--ok'
                      : 'indicador__valor--atencao'
                  }`}
                >
                  {ultimaLeitura ? `${formatarTemperatura(ultimaLeitura.temperatura)} °C` : '—'}
                </p>
                <p className="indicador__nota">
                  {horasSemColeta !== null ? `há ${formatarNumero(horasSemColeta, 0)} h` : 'sem coleta'}
                </p>
              </div>
              <div>
                <p className="indicador__rotulo">Pico do ciclo</p>
                <p className="indicador__valor">
                  {pico !== null ? `${formatarTemperatura(pico)} °C` : '—'}
                </p>
                <p className="indicador__nota">{resumo?.totalDeColetas ?? 0} coletas</p>
              </div>
              <div>
                <p className="indicador__rotulo">C/N inicial</p>
                <p className="indicador__valor">
                  {leira.data.relacao_cn_inicial
                    ? formatarNumero(leira.data.relacao_cn_inicial, 1)
                    : '—'}
                </p>
                <p className="indicador__nota">
                  {leira.data.umidade_inicial_percentual
                    ? `umidade ${formatarNumero(leira.data.umidade_inicial_percentual, 1)}%`
                    : 'sem composição'}
                </p>
              </div>
              <div>
                <p className="indicador__rotulo">Massa do lote</p>
                <p className="indicador__valor">
                  {leira.data.massa_total_kg ? formatarMassa(leira.data.massa_total_kg) : '—'}
                </p>
                <p className="indicador__nota">
                  montada em {formatarDataHora(leira.data.data_montagem)}
                </p>
              </div>
            </div>

            {resumo ? (
              <div className="linha linha--envolver" style={{ marginTop: 'var(--esp-4)' }}>
                <Selo tom={resumo.termofilicaNoPrazo ? 'ok' : 'atencao'}>
                  {resumo.termofilicaNoPrazo
                    ? '55 °C dentro de 72 h'
                    : resumo.prazoTermofilicoVencido
                      ? 'prazo de 72 h vencido'
                      : 'aguardando os 55 °C'}
                </Selo>
                {resumo.quedaBrusca ? <Selo tom="perigo">queda brusca no histórico</Selo> : null}
              </div>
            ) : null}
          </Cartao>
        ) : (
          <Esqueleto altura={180} />
        )}

        <Cartao>
          <span className="rotulo">Curva de temperatura</span>
          <div style={{ marginTop: 'var(--esp-4)' }}>
            {afericoes.isPending ? <Esqueleto altura={220} /> : null}
            {afericoes.data && afericoes.data.length > 0 ? (
              <GraficoDeTemperatura
                pontos={afericoes.data.map((afericao) => ({
                  registradoEm: afericao.registrado_em,
                  temperatura: Number(afericao.temperatura_celsius),
                }))}
              />
            ) : null}
            {afericoes.data && afericoes.data.length === 0 ? (
              <EstadoVazio
                icone="termometro"
                titulo="Nenhuma aferição nesta leira"
                acao={
                  leira.data ? (
                    <Link className="botao" to={CAMINHOS.novaAfericao(leira.data.id)}>
                      Registrar a primeira
                    </Link>
                  ) : null
                }
              >
                A curva aparece a partir da primeira coleta de temperatura.
              </EstadoVazio>
            ) : null}
          </div>
        </Cartao>

        {alertas.data && alertas.data.length > 0 ? (
          <Cartao tom="atencao">
            <span className="rotulo">Alertas da leira</span>
            <div className="pilha pilha--curta" style={{ marginTop: 'var(--esp-3)' }}>
              {alertas.data.map((alerta) => (
                <p key={alerta.id} className="texto-secundario">
                  <strong>{ROTULO_TIPO_ALERTA[alerta.tipo]}</strong> ·{' '}
                  {formatarDataHora(alerta.detectado_em)} · {alerta.mensagem}
                </p>
              ))}
            </div>
          </Cartao>
        ) : null}

        <Cartao>
          <span className="rotulo">Histórico de medições</span>
          <div style={{ marginTop: 'var(--esp-3)' }}>
            {afericoes.isPending ? <ListaEsqueleto itens={4} altura={40} /> : null}

            {afericoes.isError ? (
              <FaixaDeErro
                titulo="Não foi possível carregar as aferições"
                acoes={[{ texto: 'Tentar novamente', ao: () => void afericoes.refetch() }]}
              >
                {descreverErro(afericoes.error)}
              </FaixaDeErro>
            ) : null}

            {afericoes.data && afericoes.data.length > 0 ? (
              <div className="tabela-envolvente">
                <table className="tabela">
                  <thead>
                    <tr>
                      <th>Data / hora</th>
                      <th>Temp. °C</th>
                      <th>Umidade</th>
                      <th>Coordenadas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...afericoes.data]
                      .sort(
                        (a, b) =>
                          new Date(b.registrado_em).getTime() -
                          new Date(a.registrado_em).getTime(),
                      )
                      .map((afericao) => (
                        <tr key={afericao.id}>
                          <td className="numero">{formatarDataHora(afericao.registrado_em)}</td>
                          <td className="numero">
                            {formatarTemperatura(Number(afericao.temperatura_celsius))}
                          </td>
                          <td className="numero">
                            {afericao.umidade_percentual
                              ? `${formatarNumero(afericao.umidade_percentual, 0)}%`
                              : '—'}
                          </td>
                          <td className="numero">
                            {formatarCoordenada(afericao.latitude, afericao.longitude)}
                          </td>
                        </tr>
                      ))}
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
