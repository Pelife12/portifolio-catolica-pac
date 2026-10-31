"""índices de desempenho das consultas recorrentes (RNF02)

Revision ID: 0003_indices_de_desempenho
Revises: 0002_afericao_trava_temporal
Create Date: 2026-09-17

Cobre as duas consultas que mais crescem com o uso:

* central de alertas: filtra por status e ordena por detectado_em;
* deduplicação do motor (RF03): procura alerta da mesma leira e do mesmo tipo a
  cada aferição nova — sem índice, vira varredura da tabela a cada coleta.

O histórico de aferições por leira já é coberto por ix_afericoes_leira_registrado
(migration inicial).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0003_indices_de_desempenho"
down_revision: Union[str, None] = "0002_afericao_trava_temporal"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_alertas_status_detectado", "alertas", ["status", "detectado_em"]
    )
    op.create_index("ix_alertas_leira_tipo", "alertas", ["leira_id", "tipo"])


def downgrade() -> None:
    op.drop_index("ix_alertas_leira_tipo", table_name="alertas")
    op.drop_index("ix_alertas_status_detectado", table_name="alertas")
