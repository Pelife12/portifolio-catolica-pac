"""Composição da leira: a receita (traço) que liga leiras a resíduos e massas.

Tabela de associação com atributo próprio (massa_kg), por isso é um modelo
explícito e não apenas uma tabela secundária.
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
    from app.infrastructure.database.models.residuo import Residuo


class LeiraResiduo(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "leira_residuos"

    leira_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("leiras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    residuo_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("residuos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    massa_kg: Mapped[float] = mapped_column(sa.Numeric(12, 3), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    leira: Mapped[Leira] = relationship(back_populates="composicao")
    residuo: Mapped[Residuo] = relationship()

    __table_args__ = (
        # Um resíduo não se repete na mesma leira: soma-se a massa em um único item.
        sa.UniqueConstraint("leira_id", "residuo_id", name="residuo_unico_por_leira"),
        sa.CheckConstraint("massa_kg > 0", name="massa_positiva"),
    )
