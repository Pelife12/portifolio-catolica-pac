"""Aferição: registro de temperatura e umidade de uma leira em um instante.

Carrega os dados exigidos pela trilha de auditoria (RNF01): o timestamp real da
coleta (gerado no campo, possivelmente offline), a geolocalização do dispositivo
e o usuário responsável. O identificador do cliente (`id_cliente`) dá suporte à
sincronização idempotente do PWA (entrega de 05/11): reenvios da mesma coleta não
geram duplicatas.

A trava temporal de 24 horas (RF02) e o disparo de alertas (RF03) serão aplicados
sobre esta tabela na Sprint 2 (motor de regras).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.mixins import UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.leira import Leira
    from app.infrastructure.database.models.usuario import Usuario


class Afericao(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "afericoes"

    leira_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("leiras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    temperatura_celsius: Mapped[float] = mapped_column(sa.Numeric(5, 2), nullable=False)
    umidade_percentual: Mapped[float | None] = mapped_column(sa.Numeric(5, 2))

    # Timestamp REAL da coleta, gerado no dispositivo (base para a trava de 24h).
    registrado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    # Geolocalização capturada no momento da coleta. Obrigatória (RNF01): toda
    # aferição precisa comprovar onde foi feita, para a trilha de auditoria.
    latitude: Mapped[float] = mapped_column(sa.Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(sa.Numeric(9, 6), nullable=False)

    # UUID gerado no cliente para deduplicar reenvios na sincronização offline.
    id_cliente: Mapped[uuid.UUID | None] = mapped_column(sa.Uuid, unique=True)
    # Quando o registro chegou ao servidor (nulo enquanto só existir no dispositivo).
    sincronizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    leira: Mapped[Leira] = relationship(back_populates="afericoes")
    usuario: Mapped[Usuario] = relationship()

    __table_args__ = (
        sa.CheckConstraint(
            "temperatura_celsius >= -20 AND temperatura_celsius <= 120",
            name="temperatura_em_faixa_plausivel",
        ),
        sa.CheckConstraint(
            "umidade_percentual IS NULL OR "
            "(umidade_percentual >= 0 AND umidade_percentual <= 100)",
            name="umidade_valida",
        ),
        # Consulta recorrente do motor: histórico de uma leira em ordem de coleta.
        sa.Index("ix_afericoes_leira_registrado", "leira_id", "registrado_em"),
    )
