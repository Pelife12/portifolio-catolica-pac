/**
 * Cadastro de leira com cálculo de traço em tempo real (RF01).
 *
 * O operador monta a mistura informando resíduo e massa; a cada mudança (com um
 * atraso curto para não disparar a cada tecla) a tela pede o cálculo ao backend
 * e mostra a relação C/N e a umidade resultantes ANTES de a leira ser criada —
 * corrigir a mistura depois de montada custa retrabalho no pátio.
 */

import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import type { ItemDeComposicao, Residuo } from '@/aplicacao/contratos/tipos'
import { usarCalcularTraco, usarCriarLeira } from '@/aplicacao/hooks/usar-leiras'
import { usarResiduos } from '@/aplicacao/hooks/usar-residuos'
import { usarUsuarioAtual } from '@/aplicacao/hooks/usar-sessao'
import { formatarMassa, formatarNumero } from '@/dominio/formatacao'
import { ROTULO_CATEGORIA_RESIDUO } from '@/dominio/rotulos'
import { orientarCorrecaoCn, orientarCorrecaoUmidade } from '@/dominio/traco'
import { descreverErro } from '@/infraestrutura/http/erros'
import { Botao } from '@/ui/componentes/Botao'
import { CampoDeTexto } from '@/ui/componentes/CampoDeTexto'
import { Cartao } from '@/ui/componentes/Cartao'
import { Esqueleto } from '@/ui/componentes/Carregando'
import { FaixaDeErro } from '@/ui/componentes/FaixaDeErro'
import { Icone } from '@/ui/componentes/Icone'
import { Selo } from '@/ui/componentes/Selo'
import { Seletor } from '@/ui/componentes/Seletor'
import { usarValorAtrasado } from '@/ui/hooks/usar-valor-atrasado'
import { CAMINHOS } from '@/ui/rotas/caminhos'

interface LinhaDaComposicao {
  /** Chave local da linha: o resíduo pode estar em branco enquanto se escolhe. */
  chave: string
  residuoId: string
  massa: string
}

function linhaVazia(): LinhaDaComposicao {
  return { chave: crypto.randomUUID(), residuoId: '', massa: '' }
}

/** Data de hoje no formato aceito pelo input[type=date]. */
function hojeISO(): string {
  const agora = new Date()
  const mes = String(agora.getMonth() + 1).padStart(2, '0')
  const dia = String(agora.getDate()).padStart(2, '0')
  return `${agora.getFullYear()}-${mes}-${dia}`
}

export function NovaLeira() {
  const navegar = useNavigate()
  const { data: usuario } = usarUsuarioAtual()
  const { data: residuos, isPending: carregandoResiduos } = usarResiduos()
  const criarLeira = usarCriarLeira()
  const calcularTraco = usarCalcularTraco()

  const [codigo, definirCodigo] = useState('')
  const [dataMontagem, definirDataMontagem] = useState(hojeISO())
  const [observacoes, definirObservacoes] = useState('')
  const [linhas, definirLinhas] = useState<LinhaDaComposicao[]>([linhaVazia()])

  // Itens completos (resíduo escolhido e massa positiva) são o que o backend aceita.
  const itens = useMemo<ItemDeComposicao[]>(
    () =>
      linhas
        .map((linha) => ({
          residuo_id: linha.residuoId,
          massa_kg: Number(linha.massa.replace(',', '.')),
        }))
        .filter((item) => item.residuo_id !== '' && Number.isFinite(item.massa_kg) && item.massa_kg > 0),
    [linhas],
  )

  // Assinatura estável da composição: evita recalcular quando nada mudou de fato.
  const assinatura = useMemo(
    () => itens.map((item) => `${item.residuo_id}:${item.massa_kg}`).join('|'),
    [itens],
  )
  const assinaturaAtrasada = usarValorAtrasado(assinatura, 450)

  useEffect(() => {
    if (assinaturaAtrasada === '' || itens.length === 0) {
      calcularTraco.reset()
      return
    }
    calcularTraco.mutate(itens)
    // Dependência intencionalmente só na assinatura atrasada: `itens` e a
    // mutação trocam de identidade a cada render, e o que deve disparar um novo
    // cálculo é a mistura ter mudado de fato.
  }, [assinaturaAtrasada]) // eslint-disable-line react-hooks/exhaustive-deps

  const traco = calcularTraco.data
  const podeSalvar =
    codigo.trim().length > 0 && dataMontagem !== '' && Boolean(usuario) && !criarLeira.isPending

  function enviar() {
    if (!usuario) return
    criarLeira.mutate(
      {
        dados: {
          usina_id: usuario.usina_id,
          codigo: codigo.trim(),
          // A API espera datetime com fuso; a montagem é registrada ao meio-dia
          // local do dia informado, para não virar o dia em outro fuso.
          data_montagem: new Date(`${dataMontagem}T12:00:00`).toISOString(),
          observacoes: observacoes.trim() === '' ? null : observacoes.trim(),
        },
        itens,
      },
      { onSuccess: () => navegar(CAMINHOS.leiras) },
    )
  }

  return (
    <section>
      <button type="button" className="pagina__voltar" onClick={() => navegar(CAMINHOS.leiras)}>
        <Icone nome="seta-esquerda" tamanho={16} />
        Leiras
      </button>

      <div className="pagina__cabecalho">
        <div>
          <h1>Nova leira</h1>
          <p className="texto-secundario">Identificação e composição da mistura</p>
        </div>
      </div>

      <div className="pilha">
        <Cartao>
          <div className="pilha">
            <CampoDeTexto
              rotulo="Código da leira"
              placeholder="LR-014"
              autoCapitalize="characters"
              value={codigo}
              onChange={(evento) => definirCodigo(evento.target.value)}
              auxiliar="Como a leira é identificada na placa, no pátio."
            />
            <CampoDeTexto
              rotulo="Data de montagem"
              type="date"
              value={dataMontagem}
              max={hojeISO()}
              onChange={(evento) => definirDataMontagem(evento.target.value)}
            />
            <CampoDeTexto
              rotulo="Observações"
              placeholder="Opcional"
              value={observacoes}
              onChange={(evento) => definirObservacoes(evento.target.value)}
            />
          </div>
        </Cartao>

        <Cartao>
          <div className="linha linha--entre" style={{ marginBottom: 'var(--esp-4)' }}>
            <span className="rotulo">Composição da mistura</span>
            <span className="texto-secundario">
              {itens.length} {itens.length === 1 ? 'resíduo' : 'resíduos'}
            </span>
          </div>

          {carregandoResiduos ? (
            <Esqueleto altura={56} />
          ) : (
            <div className="pilha">
              {linhas.map((linha) => (
                <div className="composicao__item" key={linha.chave}>
                  <Seletor
                    rotulo="Resíduo"
                    textoVazio="Escolher resíduo…"
                    value={linha.residuoId}
                    opcoes={(residuos ?? []).map((residuo) => ({
                      valor: residuo.id,
                      texto: rotularResiduo(residuo),
                    }))}
                    onChange={(evento) =>
                      definirLinhas((atuais) =>
                        atuais.map((item) =>
                          item.chave === linha.chave
                            ? { ...item, residuoId: evento.target.value }
                            : item,
                        ),
                      )
                    }
                  />
                  <CampoDeTexto
                    rotulo="Massa (kg)"
                    inputMode="decimal"
                    placeholder="0"
                    value={linha.massa}
                    onChange={(evento) =>
                      definirLinhas((atuais) =>
                        atuais.map((item) =>
                          item.chave === linha.chave
                            ? { ...item, massa: evento.target.value }
                            : item,
                        ),
                      )
                    }
                  />
                  <button
                    type="button"
                    className="composicao__remover"
                    aria-label="Remover este resíduo da mistura"
                    // A última linha não é removida: a tela nunca fica sem campo.
                    disabled={linhas.length === 1}
                    onClick={() =>
                      definirLinhas((atuais) => atuais.filter((item) => item.chave !== linha.chave))
                    }
                  >
                    ×
                  </button>
                </div>
              ))}

              <Botao
                variante="secundario"
                onClick={() => definirLinhas((atuais) => [...atuais, linhaVazia()])}
              >
                Adicionar resíduo
              </Botao>
            </div>
          )}
        </Cartao>

        <Cartao tom={traco && !(traco.cn_dentro_do_ideal && traco.umidade_dentro_do_ideal) ? 'atencao' : 'normal'}>
          <div className="linha linha--entre" style={{ marginBottom: 'var(--esp-4)' }}>
            <span className="rotulo">Traço calculado</span>
            {calcularTraco.isPending ? <span className="texto-secundario">Calculando…</span> : null}
          </div>

          {!traco && !calcularTraco.isError ? (
            <p className="texto-secundario">
              Informe resíduo e massa para ver a relação C/N e a umidade da mistura.
            </p>
          ) : null}

          {calcularTraco.isError ? (
            <FaixaDeErro titulo="Não foi possível calcular o traço">
              {descreverErro(calcularTraco.error)}
            </FaixaDeErro>
          ) : null}

          {traco ? (
            <div className="pilha">
              <div className="indicadores">
                <div>
                  <p className="indicador__rotulo">Relação C/N</p>
                  <p
                    className={`indicador__valor ${
                      traco.cn_dentro_do_ideal ? 'indicador__valor--ok' : 'indicador__valor--atencao'
                    }`}
                  >
                    {formatarNumero(traco.relacao_cn, 1)}
                  </p>
                </div>
                <div>
                  <p className="indicador__rotulo">Umidade</p>
                  <p
                    className={`indicador__valor ${
                      traco.umidade_dentro_do_ideal
                        ? 'indicador__valor--ok'
                        : 'indicador__valor--atencao'
                    }`}
                  >
                    {formatarNumero(traco.umidade_percentual, 1)}%
                  </p>
                </div>
                <div>
                  <p className="indicador__rotulo">Massa total</p>
                  <p className="indicador__valor">{formatarMassa(traco.massa_total_kg)}</p>
                </div>
                <div>
                  <p className="indicador__rotulo">Massa seca</p>
                  <p className="indicador__valor">{formatarMassa(traco.massa_seca_kg)}</p>
                </div>
              </div>

              <div className="linha linha--envolver">
                <Selo tom={traco.cn_dentro_do_ideal ? 'ok' : 'atencao'}>
                  C/N {traco.cn_dentro_do_ideal ? 'ideal' : 'fora da faixa'}
                </Selo>
                <Selo tom={traco.umidade_dentro_do_ideal ? 'ok' : 'atencao'}>
                  Umidade {traco.umidade_dentro_do_ideal ? 'ideal' : 'fora da faixa'}
                </Selo>
              </div>

              <div className="pilha pilha--curta">
                <p className="texto-secundario">{orientarCorrecaoCn(Number(traco.relacao_cn))}</p>
                <p className="texto-secundario">
                  {orientarCorrecaoUmidade(Number(traco.umidade_percentual))}
                </p>
              </div>
            </div>
          ) : null}
        </Cartao>

        {criarLeira.isError ? (
          <FaixaDeErro titulo="Não foi possível cadastrar a leira">
            {descreverErro(criarLeira.error)}
          </FaixaDeErro>
        ) : null}

        {/* A leira pode ser cadastrada com o traço fora do ideal: a decisão
            agronômica é do gestor, o sistema apenas registra e avisa. */}
        <Botao grande bloco disabled={!podeSalvar} carregando={criarLeira.isPending} onClick={enviar}>
          Cadastrar leira
        </Botao>
      </div>
    </section>
  )
}

function rotularResiduo(residuo: Residuo): string {
  const categoria = ROTULO_CATEGORIA_RESIDUO[residuo.categoria]
  return `${residuo.nome} · ${categoria} · C ${formatarNumero(residuo.percentual_carbono, 0)}% / N ${formatarNumero(residuo.percentual_nitrogenio, 1)}%`
}
