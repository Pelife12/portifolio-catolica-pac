"""Enumerações de domínio persistidas como tipos ENUM nativos do PostgreSQL."""

from enum import Enum


class PapelUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    GESTOR = "gestor"
    OPERADOR = "operador"


class CategoriaResiduo(str, Enum):
    """Classificação agronômica que define o papel do resíduo no traço."""

    RICO_EM_CARBONO = "rico_em_carbono"      # "marrons": palha, serragem, folhas secas
    RICO_EM_NITROGENIO = "rico_em_nitrogenio"  # "verdes": esterco, restos de comida


class StatusLeira(str, Enum):
    EM_MONTAGEM = "em_montagem"
    ATIVA = "ativa"
    EM_MATURACAO = "em_maturacao"
    ENCERRADA = "encerrada"


class TipoAlerta(str, Enum):
    NAO_ATINGIU_TERMOFILICA = "nao_atingiu_termofilica"   # não passou de 55 °C em 72h
    QUEDA_BRUSCA_TEMPERATURA = "queda_brusca_temperatura"
    UMIDADE_FORA_DA_FAIXA = "umidade_fora_da_faixa"


class SeveridadeAlerta(str, Enum):
    INFORMATIVO = "informativo"
    ATENCAO = "atencao"
    CRITICO = "critico"


class StatusAlerta(str, Enum):
    ABERTO = "aberto"
    RECONHECIDO = "reconhecido"
    RESOLVIDO = "resolvido"


class AcaoAuditoria(str, Enum):
    CRIAR = "criar"
    ATUALIZAR = "atualizar"
    REMOVER = "remover"
    LOGIN = "login"
    EXPORTAR_LAUDO = "exportar_laudo"
