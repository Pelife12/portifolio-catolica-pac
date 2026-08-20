"""Mixins reutilizados pelos modelos: chave primária UUID e carimbos de tempo."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    """Chave primária UUID gerada na aplicação.

    UUID (em vez de sequencial) facilita a sincronização offline do PWA: o
    cliente pode gerar identificadores sem colidir com os do servidor.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid, primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Carimbos de criação e atualização, preenchidos pelo próprio banco."""

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
