"""Testes unitários da trava temporal da aferição (RF02)."""

from datetime import UTC, datetime, timedelta

import pytest

from app.domain.exceptions import AfericaoForaDaJanela
from app.domain.services.validacao_temporal import validar_janela_de_afericao

AGORA = datetime(2026, 9, 10, 12, 0, 0, tzinfo=UTC)


def test_coleta_agora_e_valida():
    validar_janela_de_afericao(AGORA, agora=AGORA, janela_horas=24)


def test_coleta_ha_23h_e_valida():
    registrado = AGORA - timedelta(hours=23)
    validar_janela_de_afericao(registrado, agora=AGORA, janela_horas=24)


def test_coleta_no_limite_de_24h_e_valida():
    registrado = AGORA - timedelta(hours=24)
    validar_janela_de_afericao(registrado, agora=AGORA, janela_horas=24)


def test_coleta_retroativa_alem_de_24h_falha():
    registrado = AGORA - timedelta(hours=24, minutes=1)
    with pytest.raises(AfericaoForaDaJanela, match="retroativa"):
        validar_janela_de_afericao(registrado, agora=AGORA, janela_horas=24)


def test_coleta_no_futuro_alem_da_tolerancia_falha():
    registrado = AGORA + timedelta(minutes=10)
    with pytest.raises(AfericaoForaDaJanela, match="futuro"):
        validar_janela_de_afericao(registrado, agora=AGORA, janela_horas=24)


def test_pequena_folga_de_futuro_e_aceita():
    # Dentro da tolerância de relógio (5 min): aceito.
    registrado = AGORA + timedelta(minutes=3)
    validar_janela_de_afericao(registrado, agora=AGORA, janela_horas=24)


def test_timestamp_sem_fuso_e_rejeitado():
    registrado_ingenuo = datetime(2026, 9, 10, 12, 0, 0)  # sem tzinfo
    with pytest.raises(AfericaoForaDaJanela, match="fuso"):
        validar_janela_de_afericao(registrado_ingenuo, agora=AGORA, janela_horas=24)
