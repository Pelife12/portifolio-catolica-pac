"""RF04 — Conclusão do ciclo termofílico para o laudo.

Regra de negócio pura que responde à pergunta do laudo: o lote cumpriu a
higienização exigida? A leira é **conforme** quando alguma leitura atinge a
temperatura mínima (55 °C) dentro do prazo após a montagem (72h). Esgotado o
prazo sem isso, é **não conforme**; antes de esgotar, o ciclo está **em
andamento** e o laudo não pode afirmar nada.

Quedas bruscas não mudam a conclusão — a higienização já ocorreu —, mas entram
no laudo como observação, porque indicam falha de manejo que o auditor precisa
ver. Reaproveita o motor de inferência (RF03) para não haver duas definições de
"queda brusca" no sistema.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

from app.domain.services.motor_de_alertas import (
    LeituraDeTemperatura,
    ParametrosDoMotor,
    TipoAnomalia,
    avaliar_leira,
)


class SituacaoDoCiclo(str, Enum):
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    EM_ANDAMENTO = "em_andamento"


@dataclass(frozen=True)
class ConclusaoDoCiclo:
    situacao: SituacaoDoCiclo
    justificativa: str
    total_de_leituras: int
    pico_celsius: Decimal | None
    pico_em: datetime | None
    # Primeira leitura que atingiu a temperatura mínima dentro do prazo.
    termofilica_atingida_em: datetime | None
    horas_ate_termofilica: Decimal | None
    quedas_bruscas: int


def concluir_ciclo(
    data_montagem: datetime,
    leituras: Sequence[LeituraDeTemperatura],
    agora: datetime,
    parametros: ParametrosDoMotor | None = None,
) -> ConclusaoDoCiclo:
    p = parametros or ParametrosDoMotor()
    ordenadas = sorted(leituras, key=lambda leitura: leitura.registrado_em)
    fim_do_prazo = data_montagem + timedelta(hours=p.prazo_termofilico_horas)

    pico = max(ordenadas, key=lambda leitura: leitura.temperatura_celsius, default=None)
    atingiu = next(
        (
            leitura
            for leitura in ordenadas
            if leitura.temperatura_celsius >= p.temperatura_minima
            and leitura.registrado_em <= fim_do_prazo
        ),
        None,
    )
    quedas = sum(
        1
        for anomalia in avaliar_leira(data_montagem, ordenadas, agora, p)
        if anomalia.tipo is TipoAnomalia.QUEDA_BRUSCA_TEMPERATURA
    )

    horas_ate = None
    if atingiu is not None:
        segundos = (atingiu.registrado_em - data_montagem).total_seconds()
        horas_ate = (Decimal(str(segundos)) / Decimal(3600)).quantize(Decimal("0.1"))

    if atingiu is not None:
        situacao = SituacaoDoCiclo.CONFORME
        justificativa = (
            f"Atingiu {atingiu.temperatura_celsius} °C {horas_ate} h após a montagem, "
            f"dentro do prazo de {p.prazo_termofilico_horas} h para a fase termofílica "
            f"(mínimo de {p.temperatura_minima} °C)."
        )
    elif agora >= fim_do_prazo:
        situacao = SituacaoDoCiclo.NAO_CONFORME
        justificativa = (
            f"Nenhuma leitura atingiu {p.temperatura_minima} °C nas primeiras "
            f"{p.prazo_termofilico_horas} h após a montagem: a higienização "
            "termofílica não foi comprovada."
        )
    else:
        situacao = SituacaoDoCiclo.EM_ANDAMENTO
        justificativa = (
            f"O prazo de {p.prazo_termofilico_horas} h ainda não terminou e nenhuma leitura "
            f"atingiu {p.temperatura_minima} °C até o momento da emissão."
        )

    return ConclusaoDoCiclo(
        situacao=situacao,
        justificativa=justificativa,
        total_de_leituras=len(ordenadas),
        pico_celsius=pico.temperatura_celsius if pico else None,
        pico_em=pico.registrado_em if pico else None,
        termofilica_atingida_em=atingiu.registrado_em if atingiu else None,
        horas_ate_termofilica=horas_ate,
        quedas_bruscas=quedas,
    )
