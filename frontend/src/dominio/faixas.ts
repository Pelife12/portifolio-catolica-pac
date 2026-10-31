/**
 * Base de conhecimento agronômica espelhada do domínio do backend.
 *
 * O backend continua sendo a autoridade: estas constantes servem apenas para
 * diagnóstico imediato na tela (o operador precisa ver "dentro da faixa" antes
 * de ter rede). Se divergirem do backend, vale o que o backend responder.
 */

export const CN_IDEAL_MINIMO = 25
export const CN_IDEAL_MAXIMO = 35

export const UMIDADE_IDEAL_MINIMA = 50
export const UMIDADE_IDEAL_MAXIMA = 60

/** RF03: a leira precisa passar disto dentro do prazo termofílico. */
export const TEMPERATURA_TERMOFILICA_MINIMA = 55
export const PRAZO_FASE_TERMOFILICA_HORAS = 72
export const QUEDA_BRUSCA_DELTA_CELSIUS = 10

/** Limites aceitos pela API para a leitura do termômetro de haste. */
export const TEMPERATURA_MINIMA = -20
export const TEMPERATURA_MAXIMA = 120

/** Passo do contador de campo: meio grau, como o termômetro de haste. */
export const PASSO_TEMPERATURA = 0.5

/** RF02: a API e o banco recusam coletas retroativas além desta janela. */
export const JANELA_RETROATIVA_HORAS = 24
