"""trava temporal e geolocalização obrigatória na aferição

Revision ID: 0002_afericao_trava_temporal
Revises: 0001_criacao_inicial
Create Date: 2026-09-10

RF02: cria um gatilho que rejeita, no próprio banco, aferições com horário de
coleta retroativo a mais de 24 horas (ou no futuro). Um CHECK não resolve porque
precisaria referenciar now(), que não é imutável — por isso um trigger.

RNF01: torna latitude e longitude obrigatórias (NOT NULL), pois toda aferição
deve comprovar a geolocalização para a trilha de auditoria.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002_afericao_trava_temporal"
down_revision: Union[str, None] = "0001_criacao_inicial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_FUNCAO = """
CREATE OR REPLACE FUNCTION fn_afericao_trava_temporal()
RETURNS trigger AS $$
BEGIN
    IF NEW.registrado_em < now() - interval '24 hours' THEN
        RAISE EXCEPTION
            'Afericao com data retroativa a mais de 24 horas nao e permitida (registrado_em=%).',
            NEW.registrado_em
            USING ERRCODE = 'check_violation';
    END IF;

    IF NEW.registrado_em > now() + interval '5 minutes' THEN
        RAISE EXCEPTION
            'Afericao com data no futuro nao e permitida (registrado_em=%).',
            NEW.registrado_em
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

_GATILHO = """
CREATE TRIGGER trg_afericao_trava_temporal
    BEFORE INSERT OR UPDATE ON afericoes
    FOR EACH ROW
    EXECUTE FUNCTION fn_afericao_trava_temporal();
"""


def upgrade() -> None:
    # RNF01: geolocalização obrigatória.
    op.alter_column("afericoes", "latitude", nullable=False)
    op.alter_column("afericoes", "longitude", nullable=False)

    # RF02: trava temporal no banco.
    op.execute(_FUNCAO)
    op.execute(_GATILHO)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_afericao_trava_temporal ON afericoes;")
    op.execute("DROP FUNCTION IF EXISTS fn_afericao_trava_temporal();")

    op.alter_column("afericoes", "longitude", nullable=True)
    op.alter_column("afericoes", "latitude", nullable=True)
