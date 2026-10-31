/** Tradução dos enums da API para o vocabulário do pátio. */

import type {
  CategoriaResiduo,
  PapelUsuario,
  SeveridadeAlerta,
  StatusAlerta,
  StatusLeira,
  TipoAlerta,
} from './enums'

export const ROTULO_STATUS_LEIRA: Record<StatusLeira, string> = {
  em_montagem: 'Em montagem',
  ativa: 'Ativa',
  em_maturacao: 'Em maturação',
  encerrada: 'Encerrada',
}

export const ROTULO_TIPO_ALERTA: Record<TipoAlerta, string> = {
  nao_atingiu_termofilica: 'Não atingiu a fase termofílica',
  queda_brusca_temperatura: 'Queda brusca de temperatura',
  umidade_fora_da_faixa: 'Umidade fora da faixa',
}

export const ROTULO_SEVERIDADE: Record<SeveridadeAlerta, string> = {
  informativo: 'Informativo',
  atencao: 'Atenção',
  critico: 'Crítico',
}

export const ROTULO_STATUS_ALERTA: Record<StatusAlerta, string> = {
  aberto: 'Aberto',
  reconhecido: 'Reconhecido',
  resolvido: 'Resolvido',
}

export const ROTULO_CATEGORIA_RESIDUO: Record<CategoriaResiduo, string> = {
  rico_em_carbono: 'Rico em carbono (marrom)',
  rico_em_nitrogenio: 'Rico em nitrogênio (verde)',
}

export const ROTULO_PAPEL: Record<PapelUsuario, string> = {
  administrador: 'Administrador',
  gestor: 'Gestor',
  operador: 'Operador',
}

/** Cor semântica de cada severidade, em token (nunca cor literal na tela). */
export const TOKEN_COR_SEVERIDADE: Record<SeveridadeAlerta, string> = {
  informativo: 'var(--acento)',
  atencao: 'var(--atencao)',
  critico: 'var(--perigo)',
}
