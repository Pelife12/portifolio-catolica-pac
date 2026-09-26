/**
 * Curva de temperatura do ciclo, em SVG.
 *
 * Desenhado à mão em vez de trazer uma biblioteca de gráficos: é uma única
 * série com uma linha de referência, e o peso do pacote no celular do pátio não
 * se justificaria. A linha dos 55 °C é o que o gestor procura ao abrir a tela.
 */

import { TEMPERATURA_TERMOFILICA_MINIMA } from '@/dominio/faixas'
import { formatarData } from '@/dominio/formatacao'

export interface PontoDaCurva {
  registradoEm: string
  temperatura: number
}

const LARGURA = 640
const ALTURA = 240
const MARGEM = { topo: 16, direita: 12, base: 28, esquerda: 38 }

export function GraficoDeTemperatura({ pontos }: { pontos: PontoDaCurva[] }) {
  if (pontos.length === 0) return null

  const ordenados = [...pontos].sort(
    (a, b) => new Date(a.registradoEm).getTime() - new Date(b.registradoEm).getTime(),
  )

  const temperaturas = ordenados.map((ponto) => ponto.temperatura)
  // A escala sempre inclui os 55 °C, senão a linha de referência sai do gráfico.
  const minimo = Math.min(...temperaturas, TEMPERATURA_TERMOFILICA_MINIMA) - 5
  const maximo = Math.max(...temperaturas, TEMPERATURA_TERMOFILICA_MINIMA) + 5

  const primeiro = new Date(ordenados[0]!.registradoEm).getTime()
  const ultimo = new Date(ordenados[ordenados.length - 1]!.registradoEm).getTime()
  const duracao = Math.max(1, ultimo - primeiro)

  const areaLargura = LARGURA - MARGEM.esquerda - MARGEM.direita
  const areaAltura = ALTURA - MARGEM.topo - MARGEM.base

  const x = (iso: string) =>
    MARGEM.esquerda + ((new Date(iso).getTime() - primeiro) / duracao) * areaLargura
  const y = (temperatura: number) =>
    MARGEM.topo + (1 - (temperatura - minimo) / (maximo - minimo)) * areaAltura

  const caminho = ordenados
    .map((ponto, indice) => `${indice === 0 ? 'M' : 'L'}${x(ponto.registradoEm).toFixed(1)},${y(ponto.temperatura).toFixed(1)}`)
    .join(' ')

  const yReferencia = y(TEMPERATURA_TERMOFILICA_MINIMA)

  return (
    <div>
      <svg
        className="grafico"
        viewBox={`0 0 ${LARGURA} ${ALTURA}`}
        role="img"
        aria-label={`Curva de temperatura com ${ordenados.length} aferições, de ${formatarData(
          ordenados[0]!.registradoEm,
        )} a ${formatarData(ordenados[ordenados.length - 1]!.registradoEm)}.`}
      >
        {/* Eixo e rótulos da escala. */}
        {[maximo, (maximo + minimo) / 2, minimo].map((valor) => (
          <g key={valor}>
            <line
              x1={MARGEM.esquerda}
              x2={LARGURA - MARGEM.direita}
              y1={y(valor)}
              y2={y(valor)}
              stroke="var(--linha)"
              strokeWidth="1"
            />
            <text
              x={MARGEM.esquerda - 8}
              y={y(valor) + 4}
              textAnchor="end"
              fontSize="11"
              fontFamily="var(--fonte-mono)"
              fill="var(--fg2)"
            >
              {Math.round(valor)}
            </text>
          </g>
        ))}

        {/* Regra do MAPA: 55 °C. */}
        <line
          x1={MARGEM.esquerda}
          x2={LARGURA - MARGEM.direita}
          y1={yReferencia}
          y2={yReferencia}
          stroke="var(--ok)"
          strokeWidth="1.5"
          strokeDasharray="6 4"
        />
        <text
          x={LARGURA - MARGEM.direita}
          y={yReferencia - 6}
          textAnchor="end"
          fontSize="11"
          fontFamily="var(--fonte-mono)"
          fill="var(--ok)"
        >
          55 °C
        </text>

        <path d={caminho} fill="none" stroke="var(--acento)" strokeWidth="2.5" strokeLinejoin="round" />

        {ordenados.map((ponto) => (
          <circle
            key={ponto.registradoEm}
            cx={x(ponto.registradoEm)}
            cy={y(ponto.temperatura)}
            r="3.5"
            fill={
              ponto.temperatura >= TEMPERATURA_TERMOFILICA_MINIMA
                ? 'var(--ok)'
                : 'var(--atencao)'
            }
          />
        ))}

        <text
          x={MARGEM.esquerda}
          y={ALTURA - 8}
          fontSize="11"
          fontFamily="var(--fonte-mono)"
          fill="var(--fg2)"
        >
          {formatarData(ordenados[0]!.registradoEm)}
        </text>
        <text
          x={LARGURA - MARGEM.direita}
          y={ALTURA - 8}
          textAnchor="end"
          fontSize="11"
          fontFamily="var(--fonte-mono)"
          fill="var(--fg2)"
        >
          {formatarData(ordenados[ordenados.length - 1]!.registradoEm)}
        </text>
      </svg>

      <div className="grafico__legenda">
        <span className="grafico__chave">
          <span className="grafico__amostra" style={{ background: 'var(--acento)' }} />
          Temperatura registrada
        </span>
        <span className="grafico__chave">
          <span className="grafico__amostra" style={{ background: 'var(--ok)' }} />
          Coleta na faixa termofílica
        </span>
        <span className="grafico__chave">
          <span className="grafico__amostra" style={{ background: 'var(--atencao)' }} />
          Coleta abaixo de 55 °C
        </span>
      </div>
    </div>
  )
}
