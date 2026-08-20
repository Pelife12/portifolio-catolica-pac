"""Usina de compostagem: a organização que opera os pátios e as leiras."""

from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.leira import Leira
    from app.infrastructure.database.models.usuario import Usuario


class Usina(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "usinas"

    nome: Mapped[str] = mapped_column(sa.String(150), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(sa.String(14), unique=True)
    endereco: Mapped[str | None] = mapped_column(sa.String(255))
    # Localização de referência da usina (o pátio). Cada leira tem a sua própria.
    latitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    ativa: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    usuarios: Mapped[list[Usuario]] = relationship(
        back_populates="usina", cascade="all, delete-orphan"
    )
    leiras: Mapped[list[Leira]] = relationship(
        back_populates="usina", cascade="all, delete-orphan"
    )
