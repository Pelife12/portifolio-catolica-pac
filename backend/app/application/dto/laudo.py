"""Dados do laudo de rastreabilidade (RF04).

Estruturas imutáveis entregues ao gerador de PDF: o gerador só formata, não
consulta nada nem decide nada. Tudo que aparece no documento passa por aqui.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.services.conclusao_do_ciclo import ConclusaoDoCiclo


@dataclass(frozen=True)
class ItemDaComposicaoDoLaudo:
    residuo: str
    massa_kg: Decimal


@dataclass(frozen=True)
class AfericaoDoLaudo:
    registrado_em: datetime
    temperatura_celsius: Decimal
    umidade_percentual: Decimal | None
    operador: str
    latitude: Decimal
    longitude: Decimal


@dataclass(frozen=True)
class AlertaDoLaudo:
    tipo: str
    severidade: str
    status: str
    mensagem: str
    detectado_em: datetime


@dataclass(frozen=True)
class DadosDoLaudo:
    numero: str
    emitido_em: datetime
    emitido_por: str
    usina: str
    usina_cnpj: str | None
    leira_codigo: str
    data_montagem: datetime
    status_da_leira: str
    relacao_cn_inicial: Decimal | None
    umidade_inicial_percentual: Decimal | None
    massa_total_kg: Decimal | None
    temperatura_minima: Decimal
    prazo_termofilico_horas: int
    conclusao: ConclusaoDoCiclo
    composicao: list[ItemDaComposicaoDoLaudo]
    afericoes: list[AfericaoDoLaudo]
    alertas: list[AlertaDoLaudo]
    # SHA-256 dos dados de origem: qualquer alteração no histórico muda o hash.
    hash_de_integridade: str


@dataclass(frozen=True)
class LaudoEmitido:
    numero: str
    nome_do_arquivo: str
    conteudo: bytes
    hash_de_integridade: str
