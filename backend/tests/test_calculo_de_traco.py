"""Testes unitários do RF01 (cálculo de traço) — regra de negócio pura."""

from decimal import Decimal

import pytest

from app.domain.exceptions import RegraDeNegocioViolada
from app.domain.services.calculo_de_traco import (
    ComponenteDaMistura,
    calcular_traco,
)


def _componente(carbono, nitrogenio, umidade, massa) -> ComponenteDaMistura:
    return ComponenteDaMistura(
        percentual_carbono=Decimal(str(carbono)),
        percentual_nitrogenio=Decimal(str(nitrogenio)),
        teor_umidade_percentual=Decimal(str(umidade)),
        massa_kg=Decimal(str(massa)),
    )


def test_calculo_com_valores_conferidos_a_mao():
    # Dois resíduos, ambos sem umidade (massa seca = massa úmida) para
    # simplificar a conferência manual:
    #   A: 100 kg, 40% C, 1% N  -> C=40,  N=1
    #   B: 100 kg, 20% C, 4% N  -> C=20,  N=4
    #   C/N = 60 / 5 = 12,0
    componentes = [
        _componente(carbono=40, nitrogenio=1, umidade=0, massa=100),
        _componente(carbono=20, nitrogenio=4, umidade=0, massa=100),
    ]

    resultado = calcular_traco(componentes)

    assert resultado.carbono_total_kg == Decimal("60.000")
    assert resultado.nitrogenio_total_kg == Decimal("5.000")
    assert resultado.relacao_cn == Decimal("12.00")
    assert resultado.massa_total_kg == Decimal("200.000")
    assert resultado.umidade_percentual == Decimal("0.00")


def test_umidade_e_massa_seca_consideram_a_agua():
    # 100 kg a 60% de umidade -> 60 kg de água, 40 kg de massa seca.
    # Carbono = 40 kg * 50% = 20 kg; Nitrogênio = 40 kg * 2% = 0,8 kg.
    componentes = [_componente(carbono=50, nitrogenio=2, umidade=60, massa=100)]

    resultado = calcular_traco(componentes)

    assert resultado.massa_seca_kg == Decimal("40.000")
    assert resultado.umidade_percentual == Decimal("60.00")
    assert resultado.carbono_total_kg == Decimal("20.000")
    assert resultado.nitrogenio_total_kg == Decimal("0.800")
    assert resultado.relacao_cn == Decimal("25.00")


def test_faixas_ideais_sao_diagnosticadas():
    # C/N = 30 (ideal 25-35) e umidade = 55% (ideal 50-60): ambos dentro.
    componentes = [_componente(carbono=30, nitrogenio=1, umidade=55, massa=100)]

    resultado = calcular_traco(componentes)

    assert resultado.cn_dentro_do_ideal is True
    assert resultado.umidade_dentro_do_ideal is True


def test_cn_fora_do_ideal_e_sinalizado():
    # Só carbono demais: C/N muito alto, fora da faixa.
    componentes = [_componente(carbono=50, nitrogenio=0.5, umidade=40, massa=100)]

    resultado = calcular_traco(componentes)

    assert resultado.relacao_cn == Decimal("100.00")
    assert resultado.cn_dentro_do_ideal is False


def test_umidade_fora_do_ideal_e_sinalizada():
    componentes = [_componente(carbono=30, nitrogenio=1, umidade=20, massa=100)]

    resultado = calcular_traco(componentes)

    assert resultado.umidade_dentro_do_ideal is False


def test_mistura_vazia_falha():
    with pytest.raises(RegraDeNegocioViolada):
        calcular_traco([])


def test_massa_nao_positiva_falha():
    with pytest.raises(RegraDeNegocioViolada):
        calcular_traco([_componente(carbono=30, nitrogenio=1, umidade=50, massa=0)])


def test_sem_nitrogenio_falha_com_mensagem_clara():
    componentes = [_componente(carbono=45, nitrogenio=0, umidade=30, massa=100)]

    with pytest.raises(RegraDeNegocioViolada, match="nitrogênio"):
        calcular_traco(componentes)


def test_relacao_cn_independe_da_ordem_dos_residuos():
    a = _componente(carbono=40, nitrogenio=1, umidade=10, massa=120)
    b = _componente(carbono=15, nitrogenio=3, umidade=70, massa=80)

    assert calcular_traco([a, b]).relacao_cn == calcular_traco([b, a]).relacao_cn
