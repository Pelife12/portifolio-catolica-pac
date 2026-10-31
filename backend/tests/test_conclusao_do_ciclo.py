"""Testes da conclusão do ciclo usada no laudo (RF04)."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.domain.services.conclusao_do_ciclo import SituacaoDoCiclo, concluir_ciclo
from app.domain.services.motor_de_alertas import LeituraDeTemperatura

MONTAGEM = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)


def leitura(horas: float, temperatura: str) -> LeituraDeTemperatura:
    return LeituraDeTemperatura(
        afericao_id=uuid.uuid4(),
        registrado_em=MONTAGEM + timedelta(hours=horas),
        temperatura_celsius=Decimal(temperatura),
    )


def test_conforme_quando_atinge_55_dentro_de_72h():
    conclusao = concluir_ciclo(
        MONTAGEM,
        [leitura(12, "41"), leitura(40, "57.5"), leitura(60, "64.2")],
        agora=MONTAGEM + timedelta(days=10),
    )

    assert conclusao.situacao is SituacaoDoCiclo.CONFORME
    assert conclusao.horas_ate_termofilica == Decimal("40.0")
    assert conclusao.pico_celsius == Decimal("64.2")
    assert conclusao.total_de_leituras == 3


def test_nao_conforme_quando_o_prazo_esgota_sem_55():
    conclusao = concluir_ciclo(
        MONTAGEM, [leitura(24, "45"), leitura(70, "52")], agora=MONTAGEM + timedelta(hours=80)
    )

    assert conclusao.situacao is SituacaoDoCiclo.NAO_CONFORME
    assert conclusao.termofilica_atingida_em is None


def test_aquecimento_depois_do_prazo_nao_torna_conforme():
    conclusao = concluir_ciclo(
        MONTAGEM, [leitura(24, "45"), leitura(90, "60")], agora=MONTAGEM + timedelta(hours=100)
    )

    assert conclusao.situacao is SituacaoDoCiclo.NAO_CONFORME


def test_em_andamento_antes_do_fim_do_prazo():
    conclusao = concluir_ciclo(MONTAGEM, [leitura(10, "38")], agora=MONTAGEM + timedelta(hours=20))

    assert conclusao.situacao is SituacaoDoCiclo.EM_ANDAMENTO


def test_quedas_bruscas_entram_como_observacao_sem_mudar_a_conclusao():
    conclusao = concluir_ciclo(
        MONTAGEM,
        [leitura(30, "62"), leitura(54, "50"), leitura(78, "58")],
        agora=MONTAGEM + timedelta(days=5),
    )

    assert conclusao.situacao is SituacaoDoCiclo.CONFORME
    assert conclusao.quedas_bruscas == 1


def test_leira_sem_leituras():
    conclusao = concluir_ciclo(MONTAGEM, [], agora=MONTAGEM + timedelta(hours=1))

    assert conclusao.situacao is SituacaoDoCiclo.EM_ANDAMENTO
    assert conclusao.pico_celsius is None
    assert conclusao.total_de_leituras == 0
