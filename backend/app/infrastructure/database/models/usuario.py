"""Usuário do sistema: operador de campo, gestor ou administrador."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import PapelUsuario
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.database.models.usina import Usina


class Usuario(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "usuarios"

    usina_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey("usinas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(sa.String(150), nullable=False)
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    # Hash da senha (nunca a senha em texto puro). Autenticação é da entrega de 27/08.
    senha_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    papel: Mapped[PapelUsuario] = mapped_column(
        sa.Enum(PapelUsuario, name="papel_usuario", create_type=False),
        nullable=False,
        default=PapelUsuario.OPERADOR,
    )
    ativo: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    usina: Mapped[Usina] = relationship(back_populates="usuarios")
