/**
 * Contratos da API v1 espelhados dos DTOs Pydantic do backend.
 *
 * Os campos `Decimal` do Pydantic chegam como string no JSON (o Pydantic
 * serializa Decimal como string para não perder precisão), por isso os valores
 * numéricos vindos da API são tipados como `string` e convertidos na borda.
 */

export type PapelUsuario = 'administrador' | 'gestor' | 'operador'
export type CategoriaResiduo = 'rico_em_carbono' | 'rico_em_nitrogenio'
export type StatusLeira = 'em_montagem' | 'ativa' | 'em_maturacao' | 'encerrada'
export type TipoAlerta =
  | 'nao_atingiu_termofilica'
  | 'queda_brusca_temperatura'
  | 'umidade_fora_da_faixa'
export type SeveridadeAlerta = 'informativo' | 'atencao' | 'critico'
export type StatusAlerta = 'aberto' | 'reconhecido' | 'resolvido'

export interface Token {
  access_token: string
  token_type: string
  expira_em_segundos: number
}

export interface Usuario {
  id: string
  usina_id: string
  nome: string
  email: string
  papel: PapelUsuario
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface Usina {
  id: string
  nome: string
  cnpj: string | null
  endereco: string | null
  latitude: string | null
  longitude: string | null
  ativa: boolean
  criado_em: string
  atualizado_em: string
}

export interface Residuo {
  id: string
  nome: string
  categoria: CategoriaResiduo
  percentual_carbono: string
  percentual_nitrogenio: string
  teor_umidade_percentual: string
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface Leira {
  id: string
  usina_id: string
  codigo: string
  data_montagem: string
  status: StatusLeira
  latitude: string | null
  longitude: string | null
  relacao_cn_inicial: string | null
  umidade_inicial_percentual: string | null
  massa_total_kg: string | null
  observacoes: string | null
  criado_por_id: string | null
  criado_em: string
  atualizado_em: string
}

export interface LeiraCriar {
  usina_id: string
  codigo: string
  data_montagem: string
  latitude?: number | null
  longitude?: number | null
  observacoes?: string | null
}

export interface ItemDeComposicao {
  residuo_id: string
  massa_kg: number
}

export interface ResultadoDoTraco {
  massa_total_kg: string
  massa_seca_kg: string
  carbono_total_kg: string
  nitrogenio_total_kg: string
  relacao_cn: string
  umidade_percentual: string
  cn_dentro_do_ideal: boolean
  umidade_dentro_do_ideal: boolean
}

export interface ItemDaComposicaoSalva {
  residuo_id: string
  residuo_nome: string
  massa_kg: string
}

export interface Afericao {
  id: string
  leira_id: string
  usuario_id: string
  temperatura_celsius: string
  umidade_percentual: string | null
  registrado_em: string
  latitude: string
  longitude: string
  id_cliente: string | null
  sincronizado_em: string
}

export interface AfericaoCriar {
  leira_id: string
  temperatura_celsius: number
  umidade_percentual?: number | null
  /** ISO 8601 COM fuso — a API recusa timestamp sem timezone (RNF01). */
  registrado_em: string
  latitude: number
  longitude: number
  /** UUID gerado no aparelho: idempotência da sincronização offline. */
  id_cliente: string
}

export interface Alerta {
  id: string
  leira_id: string
  afericao_id: string | null
  tipo: TipoAlerta
  severidade: SeveridadeAlerta
  status: StatusAlerta
  mensagem: string
  detectado_em: string
  reconhecido_por_id: string | null
  reconhecido_em: string | null
  criado_em: string
  atualizado_em: string
}

/** Corpo de erro padronizado pelo error_handlers.py do backend. */
export interface CorpoDeErro {
  erro: string
  mensagem: string
}
