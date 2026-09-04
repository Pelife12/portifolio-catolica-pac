"""Testes unitários do motor de inferência termofílico (RF03)."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.services.motor_de_alertas import (
    LeituraDeTemperatura,
    ParametrosDoMotor,
    TipoAnomalia,
    avaliar_leira,
)

MONTAGEM = datetime(2026, 9, 1, 8, 0, 0, tzinfo=UTC)
PARAMS = ParametrosDoMotor(
    temperatura_minima=Decimal("55"),
    prazo_termofilico_horas=72,
    queda_brusca_delta=Decimal("10"),
)


def _leitura(horas_apos_montagem: float, temperatura: str) -> LeituraDeTemperatura:
    return LeituraDeTemperatura(
        afericao_id=uuid.uuid4(),
        registrado_em=MONTAGEM + timedelta(hours=horas_apos_montagem),
        temperatura_celsius=Decimal(temperatura),
    )


def _tipos(anomalias) -> set[TipoAnomalia]:
    return {a.tipo for a in anomalias}


def test_leira_saudavel_nao_gera_anomalia():
    leituras = [
        _leitura(12, "50"),
        _leitura(24, "58"),
        _leitura(48, "62"),
        _leitura(72, "60"),
    ]
    agora = MONTAGEM + timedelta(hours=80)

    assert avaliar_leira(MONTAGEM, leituras, agora, PARAMS) == []


def test_nao_atingiu_55_em_72h_gera_alerta_critico():
    leituras = [_leitura(12, "40"), _leitura(48, "52"), _leitura(70, "54")]
    agora = MONTAGEM + timedelta(hours=73)  # prazo já esgotado

    anomalias = avaliar_leira(MONTAGEM, leituras, agora, PARAMS)

    assert TipoAnomalia.NAO_ATINGIU_TERMOFILICA in _tipos(anomalias)


def test_antes_de_72h_ainda_nao_alerta_falta_de_termofilia():
    # Mesmo abaixo de 55, ainda não deu o prazo: não pode concluir "não atingiu".
    leituras = [_leitura(12, "40"), _leitura(24, "50")]
    agora = MONTAGEM + timedelta(hours=30)

    anomalias = avaliar_leira(MONTAGEM, leituras, agora, PARAMS)

    assert TipoAnomalia.NAO_ATINGIU_TERMOFILICA not in _tipos(anomalias)


def test_atingiu_55_dentro_do_prazo_nao_gera_alerta():
    leituras = [_leitura(12, "40"), _leitura(40, "56"), _leitura(70, "50")]
    agora = MONTAGEM + timedelta(hours=80)

    anomalias = avaliar_leira(MONTAGEM, leituras, agora, PARAMS)

    assert TipoAnomalia.NAO_ATINGIU_TERMOFILICA not in _tipos(anomalias)


def test_queda_brusca_entre_leituras_gera_alerta_na_segunda():
    l1 = _leitura(24, "65")
    l2 = _leitura(30, "50")  # queda de 15 °C (>= 10): brusca
    leituras = [l1, l2]
    agora = MONTAGEM + timedelta(hours=35)

    anomalias = avaliar_leira(MONTAGEM, leituras, agora, PARAMS)

    quedas = [a for a in anomalias if a.tipo is TipoAnomalia.QUEDA_BRUSCA_TEMPERATURA]
    assert len(quedas) == 1
    assert quedas[0].afericao_id == l2.afericao_id


def test_queda_suave_nao_gera_alerta():
    leituras = [_leitura(24, "60"), _leitura(30, "56")]  # queda de 4 °C
    agora = MONTAGEM + timedelta(hours=35)

    anomalias = avaliar_leira(MONTAGEM, leituras, agora, PARAMS)

    assert TipoAnomalia.QUEDA_BRUSCA_TEMPERATURA not in _tipos(anomalias)


def test_avaliacao_independe_da_ordem_de_entrada():
    l1 = _leitura(24, "65")
    l2 = _leitura(30, "50")
    agora = MONTAGEM + timedelta(hours=35)

    fora_de_ordem = avaliar_leira(MONTAGEM, [l2, l1], agora, PARAMS)
    em_ordem = avaliar_leira(MONTAGEM, [l1, l2], agora, PARAMS)

    assert _tipos(fora_de_ordem) == _tipos(em_ordem)


def test_sem_leituras_e_prazo_vencido_alerta_falta_de_termofilia():
    anomalias = avaliar_leira(
        MONTAGEM, [], MONTAGEM + timedelta(hours=100), PARAMS
    )
    assert TipoAnomalia.NAO_ATINGIU_TERMOFILICA in _tipos(anomalias)
