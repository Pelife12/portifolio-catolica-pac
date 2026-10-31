"""Teste do gerador de PDF real (ReportLab)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.application.dto.laudo import (
    AfericaoDoLaudo,
    AlertaDoLaudo,
    DadosDoLaudo,
    ItemDaComposicaoDoLaudo,
)
from app.domain.services.conclusao_do_ciclo import ConclusaoDoCiclo, SituacaoDoCiclo
from app.infrastructure.relatorios.laudo_pdf_reportlab import GeradorDeLaudoReportLab

AGORA = datetime(2026, 11, 12, 15, 0, tzinfo=UTC)
MONTAGEM = AGORA - timedelta(days=12)


def dados(quantidade_de_afericoes: int, situacao=SituacaoDoCiclo.CONFORME) -> DadosDoLaudo:
    return DadosDoLaudo(
        numero="2026-1112-LR-014-A3F19C",
        emitido_em=AGORA,
        emitido_por="Marina Duarte",
        usina="Vale Verde · Un. 02",
        usina_cnpj=None,
        leira_codigo="LR-014",
        data_montagem=MONTAGEM,
        status_da_leira="ativa",
        relacao_cn_inicial=Decimal("28.4"),
        umidade_inicial_percentual=Decimal("56.2"),
        massa_total_kg=Decimal("1240"),
        temperatura_minima=Decimal("55"),
        prazo_termofilico_horas=72,
        conclusao=ConclusaoDoCiclo(
            situacao=situacao,
            justificativa="Atingiu 57.5 °C 40.0 h após a montagem.",
            total_de_leituras=quantidade_de_afericoes,
            pico_celsius=Decimal("64.2"),
            pico_em=MONTAGEM + timedelta(hours=60),
            termofilica_atingida_em=MONTAGEM + timedelta(hours=40),
            horas_ate_termofilica=Decimal("40.0"),
            quedas_bruscas=1,
        ),
        composicao=[
            ItemDaComposicaoDoLaudo("Esterco bovino", Decimal("800")),
            ItemDaComposicaoDoLaudo("Serragem", Decimal("440")),
        ],
        afericoes=[
            AfericaoDoLaudo(
                registrado_em=MONTAGEM + timedelta(hours=8 * i),
                temperatura_celsius=Decimal("40") + Decimal(i % 25),
                umidade_percentual=Decimal("55"),
                operador="Marina Duarte",
                latitude=Decimal("-26.91"),
                longitude=Decimal("-49.07"),
            )
            for i in range(quantidade_de_afericoes)
        ],
        alertas=[
            AlertaDoLaudo(
                tipo="queda_brusca_temperatura",
                severidade="atencao",
                status="resolvido",
                mensagem="Queda brusca de temperatura: de 62 °C para 50 °C.",
                detectado_em=MONTAGEM + timedelta(hours=54),
            )
        ],
        hash_de_integridade="a3f19c22" * 8,
    )


def test_gera_um_pdf_valido():
    conteudo = GeradorDeLaudoReportLab().gerar(dados(4))

    assert conteudo.startswith(b"%PDF")
    assert conteudo.rstrip().endswith(b"%%EOF")


def test_todas_as_situacoes_do_ciclo_sao_renderizaveis():
    for situacao in SituacaoDoCiclo:
        assert GeradorDeLaudoReportLab().gerar(dados(2, situacao)).startswith(b"%PDF")


def test_historico_longo_gera_documento_maior_sem_erro():
    curto = GeradorDeLaudoReportLab().gerar(dados(4))
    longo = GeradorDeLaudoReportLab().gerar(dados(150))

    # 150 linhas não cabem numa página A4: o documento quebra e cresce.
    assert len(longo) > len(curto)
