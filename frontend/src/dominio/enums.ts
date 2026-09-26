/**
 * Enumerações do domínio, espelhadas do `models/enums.py` do backend.
 *
 * Ficam aqui, e não junto dos contratos da API, porque são vocabulário de
 * negócio: o domínio precisa delas para classificar e rotular, e os contratos
 * apenas as reaproveitam.
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
