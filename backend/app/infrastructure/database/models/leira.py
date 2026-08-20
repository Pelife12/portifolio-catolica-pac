"""Leira: a pilha de compostagem (o "lote"). Unidade central de rastreabilidade."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import StatusLeira
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.afericao import Afericao
    from app.infrastructure.database.models.alerta import Alerta
    from app.infrastructure.database.models.leira_residuo import LeiraResiduo
    from app.infrastructure.database.models.usina import Usina


class Leira(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "leiras"

    usina_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("usinas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    codigo: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # Momento da montagem: marco zero para a regra das 72h da fase termofílica (RF03).
    data_montagem: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    status: Mapped[StatusLeira] = mapped_column(
        sa.Enum(StatusLeira, name="status_leira", create_type=False),
        nullable=False,
        default=StatusLeira.EM_MONTAGEM,
    )
    # Localização física da leira no pátio.
    latitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    # Traço calculado na montagem (RF01), persistido para auditoria histórica.
    relacao_cn_inicial: Mapped[float | None] = mapped_column(sa.Numeric(6, 2))
    umidade_inicial_percentual: Mapped[float | None] = mapped_column(sa.Numeric(5, 2))
    massa_total_kg: Mapped[float | None] = mapped_column(sa.Numeric(14, 3))
    observacoes: Mapped[str | None] = mapped_column(sa.Text)
    criado_por_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("usuarios.id", ondelete="SET NULL")
    )

    usina: Mapped[Usina] = relationship(back_populates="leiras")
    composicao: Mapped[list[LeiraResiduo]] = relationship(
        back_populates="leira", cascade="all, delete-orphan"
    )
    afericoes: Mapped[list[Afericao]] = relationship(
        back_populates="leira", cascade="all, delete-orphan"
    )
    alertas: Mapped[list[Alerta]] = relationship(
        back_populates="leira", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # O código da leira é único dentro de cada usina, não globalmente.
        sa.UniqueConstraint("usina_id", "codigo", name="codigo_unico_por_usina"),
    )
