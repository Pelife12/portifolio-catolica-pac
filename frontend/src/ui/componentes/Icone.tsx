/**
 * Conjunto de ícones em traço, desenhado inline.
 *
 * São poucos e fechados no conjunto usado pelo app: uma biblioteca inteira só
 * para oito glifos pesaria no carregamento do celular no pátio.
 */

export type NomeDoIcone =
  | 'alerta'
  | 'alertas'
  | 'confirmado'
  | 'gps'
  | 'gps-sem-sinal'
  | 'leira'
  | 'lua'
  | 'painel'
  | 'recarregar'
  | 'sair'
  | 'seta-esquerda'
  | 'sol'
  | 'termometro'

const TRACADOS: Record<NomeDoIcone, string> = {
  alerta: 'M12 9v4M12 17h.01M10.3 3.9 2 18a2 2 0 0 0 1.7 3h16.6a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z',
  alertas: 'M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0',
  confirmado: 'M20 6 9 17l-5-5',
  gps: 'M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.4-7 11-7 11z',
  'gps-sem-sinal': 'M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.4-7 11-7 11zM4.5 4.5l15 15',
  leira: 'M3 18h18M5 18c1.5-5 3.5-8 7-8s5.5 3 7 8M9 18c.6-2.4 1.5-4 3-4s2.4 1.6 3 4',
  lua: 'M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8z',
  painel: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
  recarregar: 'M21 12a9 9 0 1 1-3-6.7M21 4v5h-5',
  sair: 'M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M15 12H5',
  'seta-esquerda': 'M19 12H5M12 19l-7-7 7-7',
  sol: 'M12 4V2M12 22v-2M4 12H2M22 12h-2M6.3 6.3 4.9 4.9M19.1 19.1l-1.4-1.4M17.7 6.3l1.4-1.4M4.9 19.1l1.4-1.4',
  termometro: 'M14 14.8V5a2 2 0 1 0-4 0v9.8a4 4 0 1 0 4 0z',
}

interface Props {
  nome: NomeDoIcone
  tamanho?: number
  cor?: string
  /** Só informe quando o ícone carregar significado próprio, sem texto ao lado. */
  titulo?: string
}

export function Icone({ nome, tamanho = 20, cor = 'currentColor', titulo }: Props) {
  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="0 0 24 24"
      fill="none"
      stroke={cor}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      role={titulo ? 'img' : undefined}
      aria-label={titulo}
      aria-hidden={titulo ? undefined : true}
      focusable="false"
      style={{ flex: 'none' }}
    >
      <path d={TRACADOS[nome]} />
      {nome === 'sol' ? <circle cx="12" cy="12" r="4" /> : null}
      {nome === 'gps' ? <circle cx="12" cy="10" r="2.5" /> : null}
    </svg>
  )
}
