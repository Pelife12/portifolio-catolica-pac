"""RF02 — Trava temporal da aferição.

Regra de negócio pura: o horário real da coleta (`registrado_em`, gerado no
dispositivo em campo) não pode ser retroativo a mais de N horas nem estar no
futuro. Isso garante a lisura da auditoria — impede "consertar" o histórico
lançando medições com data antiga.

A mesma trava é reforçada no banco por um gatilho (ver a migration da entrega),
de modo que nenhuma via de escrita — nem a API, nem um acesso direto ao banco —
consegue burlar a janela.
"""

from datetime import datetime, timedelta

from app.domain.exceptions import AfericaoForaDaJanela

# Pequena folga para o futuro, absorvendo diferenças de relógio entre o
# dispositivo de campo (offline) e o servidor.
TOLERANCIA_FUTURO_MINUTOS = 5


def validar_janela_de_afericao(
    registrado_em: datetime,
    agora: datetime,
    janela_horas: int,
    tolerancia_futuro_minutos: int = TOLERANCIA_FUTURO_MINUTOS,
) -> None:
    """Valida o horário da coleta. Lança AfericaoForaDaJanela se estiver fora."""
    if registrado_em.tzinfo is None:
        raise AfericaoForaDaJanela(
            "O horário da coleta deve incluir o fuso horário (timestamp com timezone)."
        )

    limite_passado = agora - timedelta(hours=janela_horas)
    if registrado_em < limite_passado:
        raise AfericaoForaDaJanela(
            f"Coleta retroativa a mais de {janela_horas}h não é permitida "
            "(trava temporal de auditoria)."
        )

    if registrado_em > agora + timedelta(minutes=tolerancia_futuro_minutos):
        raise AfericaoForaDaJanela("Coleta com data no futuro não é permitida.")
