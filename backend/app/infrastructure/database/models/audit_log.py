"""Trilha de auditoria imutável (RNF01).

Registra, de forma somente-inserção, cada operação relevante do sistema com o
usuário, o momento, a origem (IP e geolocalização) e um retrato dos dados em
JSONB. A imutabilidade a nível de banco (revogar UPDATE/DELETE ou trigger de
bloqueio) é aplicada na Sprint 2, junto com o motor de regras; aqui definimos a
estrutura, sem coluna de atualização — o registro nasce e não muda.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import AcaoAuditoria
from app.infrastructure.database.models.mixins import UUIDPrimaryKeyMixin


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_log"

    # Usuário responsável pela ação; mantido mesmo se a conta for removida depois.
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.ForeignKey("usuarios.id", ondelete="SET NULL"), index=True
    )
    acao: Mapped[AcaoAuditoria] = mapped_column(
        sa.Enum(AcaoAuditoria, name="acao_auditoria", create_type=False), nullable=False
    )
    # Entidade afetada, identificada de forma genérica para cobrir qualquer tabela.
    entidade: Mapped[str] = mapped_column(sa.String(50), nullable=False, index=True)
    entidade_id: Mapped[str | None] = mapped_column(sa.String(64))
    # Retrato dos dados relevantes no momento da ação (antes/depois, payload, etc.).
    dados: Mapped[dict | None] = mapped_column(JSONB)
    endereco_ip: Mapped[str | None] = mapped_column(sa.String(45))  # comporta IPv6
    latitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(sa.Numeric(9, 6))
    registrado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
