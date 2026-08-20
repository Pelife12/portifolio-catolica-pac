"""Alerta de anomalia gerado pelo motor de inferência (RF03)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import (
    SeveridadeAlerta,
    StatusAlerta,
    TipoAlerta,
)
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.afericao import Afericao
    from app.infrastructure.database.models.leira import Leira
    from app.infrastructure.database.models.usuario import Usuario


class Alerta(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "alertas"

    leira_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("leiras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Aferição que originou o alerta, quando aplicável (queda brusca, p. ex.).
    afericao_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("afericoes.id", ondelete="SET NULL")
    )
    tipo: Mapped[TipoAlerta] = mapped_column(
        sa.Enum(TipoAlerta, name="tipo_alerta", create_type=False), nullable=False
    )
    severidade: Mapped[SeveridadeAlerta] = mapped_column(
        sa.Enum(SeveridadeAlerta, name="severidade_alerta", create_type=False),
        nullable=False,
    )
    status: Mapped[StatusAlerta] = mapped_column(
        sa.Enum(StatusAlerta, name="status_alerta", create_type=False),
        nullable=False,
        default=StatusAlerta.ABERTO,
    )
    mensagem: Mapped[str] = mapped_column(sa.Text, nullable=False)
    detectado_em: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    reconhecido_por_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    reconhecido_em: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    leira: Mapped[Leira] = relationship(back_populates="alertas")
    afericao: Mapped[Afericao | None] = relationship()
    reconhecido_por: Mapped[Usuario | None] = relationship()
