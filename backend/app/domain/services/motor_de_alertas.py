"""RF03 — Motor de inferência termofílico.

Regra de negócio pura: dado o momento de montagem da leira e o histórico de
aferições de temperatura, detecta anomalias no ciclo de compostagem:

* **Não atingiu a fase termofílica:** decorridas as primeiras N horas (72h por
  padrão) sem nenhuma leitura igual ou acima da temperatura mínima (55 °C), a
  higienização legal do material está comprometida.
* **Queda brusca de temperatura:** uma queda de X °C ou mais entre duas leituras
  consecutivas indica interrupção do processo (falta de aeração/umidade).

O motor não conhece banco nem HTTP e usa enums próprios do domínio; a camada de
aplicação os mapeia para os tipos persistidos e grava os alertas. É o alvo dos
testes unitários desta entrega.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from uuid import UUID


class TipoAnomalia(str, Enum):
    NAO_ATINGIU_TERMOFILICA = "nao_atingiu_termofilica"
    QUEDA_BRUSCA_TEMPERATURA = "queda_brusca_temperatura"


class NivelSeveridade(str, Enum):
    ATENCAO = "atencao"
    CRITICO = "critico"


@dataclass(frozen=True)
class LeituraDeTemperatura:
    afericao_id: UUID
    registrado_em: datetime
    temperatura_celsius: Decimal


@dataclass(frozen=True)
class ParametrosDoMotor:
    temperatura_minima: Decimal = Decimal("55")
    prazo_termofilico_horas: int = 72
    queda_brusca_delta: Decimal = Decimal("10")


@dataclass(frozen=True)
class AnomaliaDetectada:
    tipo: TipoAnomalia
    severidade: NivelSeveridade
    mensagem: str
    detectado_em: datetime
    afericao_id: UUID | None = None


def avaliar_leira(
    data_montagem: datetime,
    leituras: Sequence[LeituraDeTemperatura],
    agora: datetime,
    parametros: ParametrosDoMotor | None = None,
) -> list[AnomaliaDetectada]:
    """Retorna as anomalias detectadas para a leira (lista vazia se estiver sadia)."""
    parametros = parametros or ParametrosDoMotor()
    anomalias: list[AnomaliaDetectada] = []
    ordenadas = sorted(leituras, key=lambda leitura: leitura.registrado_em)

    anomalias.extend(_avaliar_fase_termofilica(data_montagem, ordenadas, agora, parametros))
    anomalias.extend(_avaliar_quedas_bruscas(ordenadas, parametros))
    return anomalias


def _avaliar_fase_termofilica(
    data_montagem: datetime,
    ordenadas: Sequence[LeituraDeTemperatura],
    agora: datetime,
    p: ParametrosDoMotor,
) -> list[AnomaliaDetectada]:
    fim_prazo = data_montagem + timedelta(hours=p.prazo_termofilico_horas)
    # Só é possível concluir que "não atingiu" depois que o prazo se esgota.
    if agora < fim_prazo:
        return []

    atingiu = any(
        leitura.temperatura_celsius >= p.temperatura_minima
        and leitura.registrado_em <= fim_prazo
        for leitura in ordenadas
    )
    if atingiu:
        return []

    return [
        AnomaliaDetectada(
            tipo=TipoAnomalia.NAO_ATINGIU_TERMOFILICA,
            severidade=NivelSeveridade.CRITICO,
            mensagem=(
                f"A leira não atingiu {p.temperatura_minima} °C nas primeiras "
                f"{p.prazo_termofilico_horas}h após a montagem; a higienização "
                "termofílica está comprometida."
            ),
            detectado_em=fim_prazo,
        )
    ]


def _avaliar_quedas_bruscas(
    ordenadas: Sequence[LeituraDeTemperatura], p: ParametrosDoMotor
) -> list[AnomaliaDetectada]:
    anomalias: list[AnomaliaDetectada] = []
    for anterior, atual in zip(ordenadas, ordenadas[1:]):
        queda = anterior.temperatura_celsius - atual.temperatura_celsius
        if queda >= p.queda_brusca_delta:
            anomalias.append(
                AnomaliaDetectada(
                    tipo=TipoAnomalia.QUEDA_BRUSCA_TEMPERATURA,
                    severidade=NivelSeveridade.ATENCAO,
                    mensagem=(
                        f"Queda brusca de temperatura: de {anterior.temperatura_celsius} °C "
                        f"para {atual.temperatura_celsius} °C (-{queda} °C) entre leituras "
                        "consecutivas."
                    ),
                    detectado_em=atual.registrado_em,
                    afericao_id=atual.afericao_id,
                )
            )
    return anomalias
