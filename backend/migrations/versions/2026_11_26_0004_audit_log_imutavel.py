"""trilha de auditoria imutável (RNF01)

Revision ID: 0004_audit_log_imutavel
Revises: 0003_indices_de_desempenho
Create Date: 2026-11-26

O modelo do audit_log já nasceu sem coluna de atualização; aqui a regra passa a
valer no banco: UPDATE e DELETE são recusados por gatilho, qualquer que seja o
cliente (a API, um script ou alguém no psql). Correção legítima de auditoria é
um novo registro, nunca a alteração do antigo.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0004_audit_log_imutavel"
down_revision: Union[str, None] = "0003_indices_de_desempenho"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_FUNCAO = """
CREATE OR REPLACE FUNCTION fn_audit_log_somente_insercao()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_log e somente insercao: % nao permitido.', TG_OP
        USING ERRCODE = 'insufficient_privilege';
END;
$$ LANGUAGE plpgsql;
"""

_GATILHO = """
CREATE TRIGGER trg_audit_log_somente_insercao
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_log_somente_insercao();
"""


def upgrade() -> None:
    op.execute(_FUNCAO)
    op.execute(_GATILHO)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_somente_insercao ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS fn_audit_log_somente_insercao();")
