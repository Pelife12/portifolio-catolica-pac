/**
 * Contador de temperatura de campo.
 *
 * O componente central do app: é onde o operador passa o dia. Passo de 0,5 °C,
 * alvos de 72px, toque longo com aceleração e leitura em 52px para ser lida de
 * braço estendido, sob sol.
 */

import { useId } from 'react'

import { PASSO_TEMPERATURA, TEMPERATURA_MAXIMA, TEMPERATURA_MINIMA } from '@/dominio/faixas'
import {
  ajustarTemperatura,
  classificarTemperatura,
  descreverTemperatura,
  formatarTemperatura,
} from '@/dominio/temperatura'
import { usarRepeticaoPorToque } from '@/ui/hooks/usar-repeticao-por-toque'

interface Props {
  valor: number
  aoMudar: (valor: number) => void
  desabilitado?: boolean
}

const CLASSE_POR_FASE = {
  criogenica: '',
  mesofilica: 'contador__valor--atencao',
  termofilica: 'contador__valor--ok',
  excessiva: 'contador__valor--perigo',
} as const

export function ContadorDeTemperatura({ valor, aoMudar, desabilitado = false }: Props) {
  const idLeitura = useId()
  const fase = classificarTemperatura(valor)

  const diminuir = usarRepeticaoPorToque(() => aoMudar(ajustarTemperatura(valor, -1)))
  const aumentar = usarRepeticaoPorToque(() => aoMudar(ajustarTemperatura(valor, +1)))

  return (
    <div>
      <span className="rotulo" id={`${idLeitura}-rotulo`}>
        Temperatura
      </span>

      <div className="contador">
        <BotaoDePasso
          sinal="−"
          descricao={`Diminuir ${PASSO_TEMPERATURA} grau`}
          desabilitado={desabilitado || valor <= TEMPERATURA_MINIMA}
          repeticao={diminuir}
        />

        <div className="contador__leitura">
          {/* aria-live: o leitor de tela acompanha a contagem sem reler a tela. */}
          <output
            className={`contador__valor ${CLASSE_POR_FASE[fase]}`}
            aria-live="polite"
            aria-labelledby={`${idLeitura}-rotulo`}
          >
            {formatarTemperatura(valor)}
          </output>
          <p className="contador__unidade">°C · {descreverTemperatura(valor)}</p>
        </div>

        <BotaoDePasso
          sinal="+"
          descricao={`Aumentar ${PASSO_TEMPERATURA} grau`}
          desabilitado={desabilitado || valor >= TEMPERATURA_MAXIMA}
          repeticao={aumentar}
        />
      </div>

      <p className="contador__nota">Passo de 0,5 °C. Toque longo acelera.</p>
    </div>
  )
}

function BotaoDePasso({
  sinal,
  descricao,
  desabilitado,
  repeticao,
}: {
  sinal: string
  descricao: string
  desabilitado: boolean
  repeticao: { aoPressionar: () => void; aoSoltar: () => void }
}) {
  return (
    <button
      type="button"
      className="contador__passo"
      aria-label={descricao}
      disabled={desabilitado}
      // onPointerDown cobre dedo, caneta e mouse com um só par de eventos;
      // onPointerLeave solta a repetição se o dedo escorregar para fora do botão.
      onPointerDown={repeticao.aoPressionar}
      onPointerUp={repeticao.aoSoltar}
      onPointerLeave={repeticao.aoSoltar}
      onPointerCancel={repeticao.aoSoltar}
      // Teclado: espaço/enter disparam click; o passo único basta.
      onKeyDown={(evento) => {
        if (evento.key === 'Enter' || evento.key === ' ') {
          evento.preventDefault()
          repeticao.aoPressionar()
          repeticao.aoSoltar()
        }
      }}
      // Evita o menu de contexto do toque longo no Android.
      onContextMenu={(evento) => evento.preventDefault()}
    >
      {sinal}
    </button>
  )
}
