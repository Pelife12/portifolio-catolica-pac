/**
 * Coleta de aferição no pátio (RF02 + RNF01).
 *
 * Tela de uso mais intenso do sistema. Três dados saem daqui: temperatura,
 * umidade (opcional) e o carimbo de auditoria — momento da coleta com fuso,
 * geolocalização do aparelho e o usuário, que vem do token e nunca do corpo.
 *
 * A trava de 24h é verificada antes do envio para o operador não perder a
 * coleta: a recusa definitiva é do servidor, mas avisar aqui evita a viagem.
 */

import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { usarRegistrarAfericao } from '@/aplicacao/hooks/usar-afericoes'
import { usarLeira } from '@/aplicacao/hooks/usar-leiras'
import { usarLocalizacao } from '@/aplicacao/hooks/usar-localizacao'
import { diasDesde, formatarCoordenada, formatarHora } from '@/dominio/formatacao'
import { avaliarJanela, explicarJanela } from '@/dominio/janela-temporal'
import { descreverUmidade, interpretarUmidadeDigitada } from '@/dominio/umidade'
import { descreverErro, ErroDeApi } from '@/infraestrutura/http/erros'
import { Botao } from '@/ui/componentes/Botao'
import { CampoDeTexto } from '@/ui/componentes/CampoDeTexto'
import { Cartao } from '@/ui/componentes/Cartao'
import { ContadorDeTemperatura } from '@/ui/componentes/ContadorDeTemperatura'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Icone } from '@/ui/componentes/Icone'
import { CAMINHOS } from '@/ui/rotas/caminhos'

/** Ponto de partida do contador: meio da faixa termofílica, perto do esperado. */
const TEMPERATURA_INICIAL = 55

/** Converte a data local para o formato do input[type=datetime-local]. */
function paraCampoLocal(data: Date): string {
  const p = (valor: number) => String(valor).padStart(2, '0')
  return `${data.getFullYear()}-${p(data.getMonth() + 1)}-${p(data.getDate())}T${p(data.getHours())}:${p(data.getMinutes())}`
}

export function NovaAfericao() {
  const { leiraId } = useParams<{ leiraId: string }>()
  const navegar = useNavigate()
  const { data: leira } = usarLeira(leiraId)
  const localizacao = usarLocalizacao()
  const registrar = usarRegistrarAfericao()

  const [temperatura, definirTemperatura] = useState(TEMPERATURA_INICIAL)
  const [umidadeTexto, definirUmidadeTexto] = useState('')
  const [momento, definirMomento] = useState(() => paraCampoLocal(new Date()))

  /**
   * UUID do cliente, estável enquanto a tela viver: se o envio falhar e o
   * operador tentar de novo, o servidor reconhece o reenvio e não duplica a
   * coleta (idempotência que a Sprint 4 vai reaproveitar na fila offline).
   */
  const [idCliente, definirIdCliente] = useState(() => crypto.randomUUID())

  const umidade = interpretarUmidadeDigitada(umidadeTexto)
  const umidadeInvalida = umidadeTexto.trim() !== '' && umidade === null

  const dataDaColeta = useMemo(() => new Date(momento), [momento])
  const situacaoDaJanela = avaliarJanela(dataDaColeta)
  const avisoDaJanela = explicarJanela(situacaoDaJanela)

  // Relógio do campo de momento: enquanto o operador não editar, acompanha a
  // hora atual, para o carimbo não ficar velho se a tela ficar aberta.
  const [momentoEditado, definirMomentoEditado] = useState(false)
  useEffect(() => {
    if (momentoEditado) return
    const relogio = setInterval(() => definirMomento(paraCampoLocal(new Date())), 30_000)
    return () => clearInterval(relogio)
  }, [momentoEditado])

  const temGps = localizacao.coordenada !== null
  const podeEnviar =
    Boolean(leiraId) && temGps && !umidadeInvalida && situacaoDaJanela === 'dentro'

  function enviar() {
    if (!leiraId || !localizacao.coordenada) return
    registrar.mutate(
      {
        leira_id: leiraId,
        temperatura_celsius: temperatura,
        umidade_percentual: umidade,
        // toISOString devolve UTC com o "Z": a API exige fuso explícito (RNF01).
        registrado_em: dataDaColeta.toISOString(),
        latitude: localizacao.coordenada.latitude,
        longitude: localizacao.coordenada.longitude,
        id_cliente: idCliente,
      },
      {
        onSuccess: (afericao) => {
          // Novo id para a próxima coleta desta sessão.
          definirIdCliente(crypto.randomUUID())
          navegar(CAMINHOS.afericaoRegistrada(leiraId), { state: { afericao } })
        },
      },
    )
  }

  const erroDeTrava = registrar.error instanceof ErroDeApi && registrar.error.travaTemporal

  return (
    <section>
      <button type="button" className="pagina__voltar" onClick={() => navegar(CAMINHOS.leiras)}>
        <Icone nome="seta-esquerda" tamanho={16} />
        Leiras
      </button>

      <div className="pagina__cabecalho">
        <div>
          <h1>Nova aferição</h1>
          <p className="casca__subtitulo">
            {leira
              ? `${leira.codigo} · dia ${diasDesde(leira.data_montagem)} do ciclo`
              : 'Carregando leira…'}
          </p>
        </div>
      </div>

      <div className="pilha">
        <Cartao>
          <ContadorDeTemperatura
            valor={temperatura}
            aoMudar={definirTemperatura}
            desabilitado={registrar.isPending}
          />
        </Cartao>

        <Cartao>
          <CampoDeTexto
            rotulo="Umidade"
            numerico
            inputMode="decimal"
            placeholder="55"
            sufixo={
              umidade !== null ? `% · ${descreverUmidade(umidade)}` : '% · opcional'
            }
            value={umidadeTexto}
            onChange={(evento) => definirUmidadeTexto(evento.target.value)}
            erro={umidadeInvalida ? 'Informe um valor entre 0 e 100.' : null}
          />
        </Cartao>

        <Cartao>
          <div className="pilha pilha--curta">
            <CampoDeTexto
              rotulo="Momento da coleta"
              type="datetime-local"
              value={momento}
              onChange={(evento) => {
                definirMomentoEditado(true)
                definirMomento(evento.target.value)
              }}
              auxiliar={
                momentoEditado
                  ? 'Carimbo que vai para a trilha de auditoria.'
                  : 'Acompanha a hora do aparelho até você editar.'
              }
              erro={avisoDaJanela}
            />
          </div>
        </Cartao>

        {localizacao.estado === 'falhou' && localizacao.erro ? (
          <FaixaDeErro
            titulo="GPS indisponível"
            acoes={[
              { texto: 'Tentar novamente', ao: localizacao.capturar, variante: 'primario' },
            ]}
          >
            {localizacao.erro.message} A coleta exige a localização para entrar na
            trilha de auditoria.
          </FaixaDeErro>
        ) : (
          <div className="linha texto-secundario" style={{ padding: '0 2px' }}>
            <Icone nome={temGps ? 'gps' : 'gps-sem-sinal'} tamanho={18} />
            {localizacao.coordenada ? (
              <span>
                GPS capturado · {formatarHora(localizacao.coordenada.capturadoEm.toISOString())}
                {localizacao.coordenada.precisaoMetros !== null
                  ? ` · ±${localizacao.coordenada.precisaoMetros} m`
                  : ''}
                {' · '}
                <span className="mono">
                  {formatarCoordenada(
                    localizacao.coordenada.latitude,
                    localizacao.coordenada.longitude,
                  )}
                </span>
              </span>
            ) : (
              <span>Procurando sinal de GPS…</span>
            )}
          </div>
        )}

        {registrar.isError ? (
          <FaixaDeErro
            titulo={erroDeTrava ? 'Coleta recusada · trava de 24 h' : 'Não foi possível registrar'}
            acoes={
              erroDeTrava
                ? [
                    {
                      texto: 'Corrigir o momento',
                      ao: () => {
                        definirMomentoEditado(false)
                        definirMomento(paraCampoLocal(new Date()))
                        registrar.reset()
                      },
                      variante: 'primario',
                    },
                  ]
                : [{ texto: 'Tentar novamente', ao: enviar, variante: 'primario' }]
            }
          >
            {descreverErro(registrar.error)}
          </FaixaDeErro>
        ) : null}

        <Botao
          grande
          bloco
          disabled={!podeEnviar}
          carregando={registrar.isPending}
          onClick={enviar}
        >
          Registrar aferição
        </Botao>

        {!temGps && localizacao.estado !== 'falhou' ? (
          <p className="texto-secundario" style={{ textAlign: 'center' }}>
            O registro libera assim que o GPS responder.
          </p>
        ) : null}
      </div>
    </section>
  )
}
