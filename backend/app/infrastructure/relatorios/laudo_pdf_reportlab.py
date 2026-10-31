"""Gerador do laudo em PDF com ReportLab (RF04).

Segue o artboard "Laudo PDF" do canvas de design: tema claro fixo (o laudo é
impresso e arquivado), hierarquia fiscal — número e emissão no topo, resumo do
lote, faixa de conclusão, tabelas e, no rodapé, o hash de integridade e a linha
de assinatura. Usa as fontes padrão do PDF (Helvetica), que cobrem os acentos
do português sem embutir arquivo de fonte.
"""

from datetime import datetime
from decimal import Decimal
from io import BytesIO
from zoneinfo import ZoneInfo

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.application.dto.laudo import DadosDoLaudo
from app.application.ports.relatorios import GeradorDeLaudo
from app.domain.services.conclusao_do_ciclo import SituacaoDoCiclo

FUSO = ZoneInfo("America/Sao_Paulo")

# Paleta do canvas convertida para RGB (tema claro).
TINTA = colors.HexColor("#1b2430")
TINTA_SECUNDARIA = colors.HexColor("#4d5866")
LINHA = colors.HexColor("#c4cad3")
ACENTO = colors.HexColor("#12609f")
OK = colors.HexColor("#1f7a4a")
ATENCAO = colors.HexColor("#8a5a00")
PERIGO = colors.HexColor("#b3261e")

_COR_POR_SITUACAO = {
    SituacaoDoCiclo.CONFORME: OK,
    SituacaoDoCiclo.NAO_CONFORME: PERIGO,
    SituacaoDoCiclo.EM_ANDAMENTO: ATENCAO,
}
_TITULO_POR_SITUACAO = {
    SituacaoDoCiclo.CONFORME: "Conforme · fase termofílica cumprida",
    SituacaoDoCiclo.NAO_CONFORME: "Não conforme · fase termofílica não comprovada",
    SituacaoDoCiclo.EM_ANDAMENTO: "Em andamento · ciclo ainda sem conclusão",
}
_ROTULO_TIPO_ALERTA = {
    "nao_atingiu_termofilica": "Não atingiu a fase termofílica",
    "queda_brusca_temperatura": "Queda brusca de temperatura",
    "umidade_fora_da_faixa": "Umidade fora da faixa",
}
_ROTULO_STATUS_LEIRA = {
    "em_montagem": "Em montagem",
    "ativa": "Ativa",
    "em_maturacao": "Em maturação",
    "encerrada": "Encerrada",
}

_ESTILOS = {
    "titulo": ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=TINTA),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Helvetica", fontSize=8.5, leading=11, textColor=TINTA_SECUNDARIA),
    "numero": ParagraphStyle("numero", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=TINTA, alignment=TA_RIGHT),
    "emissao": ParagraphStyle("emissao", fontName="Helvetica", fontSize=8.5, leading=11, textColor=TINTA_SECUNDARIA, alignment=TA_RIGHT),
    "rotulo": ParagraphStyle("rotulo", fontName="Helvetica", fontSize=7.5, leading=9, textColor=TINTA_SECUNDARIA),
    "valor": ParagraphStyle("valor", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TINTA),
    "secao": ParagraphStyle("secao", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=TINTA_SECUNDARIA, spaceBefore=10, spaceAfter=4),
    "corpo": ParagraphStyle("corpo", fontName="Helvetica", fontSize=9, leading=12, textColor=TINTA),
    "nota": ParagraphStyle("nota", fontName="Helvetica", fontSize=8, leading=10.5, textColor=TINTA_SECUNDARIA),
    "celula": ParagraphStyle("celula", fontName="Helvetica", fontSize=8, leading=10, textColor=TINTA),
}


def _data_hora(valor: datetime) -> str:
    return valor.astimezone(FUSO).strftime("%d/%m/%Y %H:%M")


def _data(valor: datetime) -> str:
    return valor.astimezone(FUSO).strftime("%d/%m/%Y")


def _numero(valor: Decimal | None, casas: int = 1, sufixo: str = "") -> str:
    if valor is None:
        return "—"
    texto = f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{texto}{sufixo}"


class GeradorDeLaudoReportLab(GeradorDeLaudo):
    def gerar(self, dados: DadosDoLaudo) -> bytes:
        destino = BytesIO()
        documento = SimpleDocTemplate(
            destino,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=18 * mm,
            title=f"Laudo de rastreabilidade {dados.numero}",
            author="Aferra · Sistema de rastreabilidade de compostagem",
            subject=f"Leira {dados.leira_codigo}",
        )
        largura = documento.width

        def rodape(canvas, doc) -> None:
            canvas.saveState()
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(TINTA_SECUNDARIA)
            canvas.drawString(18 * mm, 10 * mm, f"Laudo Nº {dados.numero}")
            canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Página {doc.page}")
            canvas.restoreState()

        historia = [
            self._cabecalho(dados, largura),
            Spacer(1, 10),
            self._resumo(dados, largura),
            Spacer(1, 10),
            self._faixa_de_conclusao(dados, largura),
            *self._composicao(dados, largura),
            *self._afericoes(dados, largura),
            *self._alertas(dados, largura),
            Spacer(1, 16),
            self._fechamento(dados, largura),
        ]
        documento.build(historia, onFirstPage=rodape, onLaterPages=rodape)
        return destino.getvalue()

    # ------------------------------------------------------------------
    def _cabecalho(self, dados: DadosDoLaudo, largura: float) -> Table:
        marca = Table(
            [[Paragraph('<font color="white"><b>A</b></font>', _ESTILOS["valor"])]],
            colWidths=[11 * mm],
            rowHeights=[11 * mm],
        )
        marca.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), ACENTO),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        identificacao = [
            Paragraph("Laudo de rastreabilidade de compostagem", _ESTILOS["titulo"]),
            Paragraph("Conformidade da fase termofílica · MAPA", _ESTILOS["subtitulo"]),
        ]
        numero = [
            Paragraph(f"Nº {dados.numero}", _ESTILOS["numero"]),
            Paragraph(f"Emissão {_data_hora(dados.emitido_em)}", _ESTILOS["emissao"]),
        ]
        tabela = Table(
            [[marca, identificacao, numero]],
            colWidths=[14 * mm, largura - 14 * mm - 62 * mm, 62 * mm],
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEBELOW", (0, 0), (-1, -1), 1.5, TINTA),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0, 0), (0, 0), 0),
                ]
            )
        )
        return tabela

    def _resumo(self, dados: DadosDoLaudo, largura: float) -> Table:
        def campo(rotulo: str, valor: str) -> list[Paragraph]:
            return [Paragraph(rotulo.upper(), _ESTILOS["rotulo"]), Paragraph(valor, _ESTILOS["valor"])]

        usina = dados.usina if not dados.usina_cnpj else f"{dados.usina} · CNPJ {dados.usina_cnpj}"
        linhas = [
            [
                campo("Leira", dados.leira_codigo),
                campo("Usina", usina),
                campo("Montagem", _data(dados.data_montagem)),
                campo("Massa do lote", _numero(dados.massa_total_kg, 0, " kg")),
            ],
            [
                campo("Situação da leira", _ROTULO_STATUS_LEIRA.get(dados.status_da_leira, dados.status_da_leira)),
                campo("C/N inicial", _numero(dados.relacao_cn_inicial, 1)),
                campo("Umidade inicial", _numero(dados.umidade_inicial_percentual, 1, "%")),
                campo("Pico registrado", _numero(dados.conclusao.pico_celsius, 1, " °C")),
            ],
        ]
        tabela = Table(linhas, colWidths=[largura / 4] * 4)
        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return tabela

    def _faixa_de_conclusao(self, dados: DadosDoLaudo, largura: float) -> Table:
        cor = _COR_POR_SITUACAO[dados.conclusao.situacao]
        titulo = ParagraphStyle("faixa", parent=_ESTILOS["valor"], textColor=cor)
        conteudo = [
            Paragraph(_TITULO_POR_SITUACAO[dados.conclusao.situacao], titulo),
            Paragraph(dados.conclusao.justificativa, _ESTILOS["corpo"]),
        ]
        if dados.conclusao.quedas_bruscas:
            conteudo.append(
                Paragraph(
                    f"Observação: {dados.conclusao.quedas_bruscas} queda(s) brusca(s) de "
                    "temperatura no histórico, indicando falha de aeração ou umidade.",
                    _ESTILOS["nota"],
                )
            )
        faixa = Table([[conteudo]], colWidths=[largura])
        faixa.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, cor),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return faixa

    def _tabela(self, cabecalho: list[str], linhas: list[list[str]], larguras: list[float]) -> Table:
        corpo = [[Paragraph(texto.upper(), _ESTILOS["rotulo"]) for texto in cabecalho]]
        corpo += [[Paragraph(celula, _ESTILOS["celula"]) for celula in linha] for linha in linhas]
        # repeatRows: o cabeçalho reaparece se a tabela quebrar de página.
        tabela = Table(corpo, colWidths=larguras, repeatRows=1)
        tabela.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.75, LINHA),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINHA),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return tabela

    def _composicao(self, dados: DadosDoLaudo, largura: float) -> list:
        if not dados.composicao:
            return []
        linhas = [[item.residuo, _numero(item.massa_kg, 1, " kg")] for item in dados.composicao]
        return [
            Paragraph("COMPOSIÇÃO DA MISTURA (TRAÇO INICIAL)", _ESTILOS["secao"]),
            self._tabela(["Resíduo", "Massa"], linhas, [largura * 0.7, largura * 0.3]),
        ]

    def _afericoes(self, dados: DadosDoLaudo, largura: float) -> list:
        titulo = Paragraph(
            f"HISTÓRICO DE AFERIÇÕES · {len(dados.afericoes)} REGISTROS", _ESTILOS["secao"]
        )
        if not dados.afericoes:
            return [titulo, Paragraph("Nenhuma aferição registrada para esta leira.", _ESTILOS["nota"])]
        linhas = [
            [
                _data_hora(a.registrado_em),
                _numero(a.temperatura_celsius, 1),
                _numero(a.umidade_percentual, 0, "%"),
                a.operador,
                f"{a.latitude:.5f}, {a.longitude:.5f}",
            ]
            for a in dados.afericoes
        ]
        return [
            titulo,
            self._tabela(
                ["Data / hora", "Temp. °C", "Umidade", "Operador", "Coordenadas"],
                linhas,
                [largura * 0.2, largura * 0.12, largura * 0.12, largura * 0.28, largura * 0.28],
            ),
        ]

    def _alertas(self, dados: DadosDoLaudo, largura: float) -> list:
        titulo = Paragraph("ALERTAS DO MOTOR DE INFERÊNCIA", _ESTILOS["secao"])
        if not dados.alertas:
            return [titulo, Paragraph("Nenhuma anomalia detectada no ciclo.", _ESTILOS["nota"])]
        linhas = [
            [
                _data_hora(alerta.detectado_em),
                _ROTULO_TIPO_ALERTA.get(alerta.tipo, alerta.tipo),
                alerta.status.capitalize(),
                alerta.mensagem,
            ]
            for alerta in dados.alertas
        ]
        return [
            titulo,
            self._tabela(
                ["Detectado em", "Tipo", "Situação", "Descrição"],
                linhas,
                [largura * 0.18, largura * 0.22, largura * 0.12, largura * 0.48],
            ),
        ]

    def _fechamento(self, dados: DadosDoLaudo, largura: float) -> KeepTogether:
        integridade = [
            Paragraph("INTEGRIDADE · SHA-256", _ESTILOS["rotulo"]),
            Paragraph(dados.hash_de_integridade[:32], _ESTILOS["nota"]),
            Paragraph(dados.hash_de_integridade[32:], _ESTILOS["nota"]),
            Spacer(1, 4),
            Paragraph(
                f"Regra aplicada: mínimo de {_numero(dados.temperatura_minima, 0)} °C em até "
                f"{dados.prazo_termofilico_horas} h após a montagem.",
                _ESTILOS["nota"],
            ),
        ]
        assinatura = [
            Spacer(1, 18),
            Paragraph("_" * 38, _ESTILOS["nota"]),
            Paragraph(dados.emitido_por, _ESTILOS["valor"]),
            Paragraph("Responsável técnico pela emissão", _ESTILOS["nota"]),
        ]
        tabela = Table([[integridade, assinatura]], colWidths=[largura * 0.55, largura * 0.45])
        tabela.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.75, LINHA),
                    ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                    ("LEFTPADDING", (0, 0), (0, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return KeepTogether([tabela])
