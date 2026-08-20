"""criação inicial do schema

Revision ID: 0001_criacao_inicial
Revises:
Create Date: 2026-08-13

Cria o schema completo do sistema: usinas, usuários, resíduos, leiras e sua
composição (traço), aferições, alertas e a trilha de auditoria, além dos tipos
ENUM de domínio.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_criacao_inicial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tipos ENUM nativos do PostgreSQL. create_type=False: criamos/removemos
# explicitamente no upgrade/downgrade para controlar a ordem.
papel_usuario = postgresql.ENUM(
    "administrador", "gestor", "operador",
    name="papel_usuario", create_type=False,
)
categoria_residuo = postgresql.ENUM(
    "rico_em_carbono", "rico_em_nitrogenio",
    name="categoria_residuo", create_type=False,
)
status_leira = postgresql.ENUM(
    "em_montagem", "ativa", "em_maturacao", "encerrada",
    name="status_leira", create_type=False,
)
tipo_alerta = postgresql.ENUM(
    "nao_atingiu_termofilica", "queda_brusca_temperatura", "umidade_fora_da_faixa",
    name="tipo_alerta", create_type=False,
)
severidade_alerta = postgresql.ENUM(
    "informativo", "atencao", "critico",
    name="severidade_alerta", create_type=False,
)
status_alerta = postgresql.ENUM(
    "aberto", "reconhecido", "resolvido",
    name="status_alerta", create_type=False,
)
acao_auditoria = postgresql.ENUM(
    "criar", "atualizar", "remover", "login", "exportar_laudo",
    name="acao_auditoria", create_type=False,
)

_ENUMS = (
    papel_usuario, categoria_residuo, status_leira, tipo_alerta,
    severidade_alerta, status_alerta, acao_auditoria,
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum in _ENUMS:
        enum.create(bind, checkfirst=True)

    op.create_table(
        "usinas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("endereco", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_usinas"),
        sa.UniqueConstraint("cnpj", name="uq_usinas_cnpj"),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usina_id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("papel", papel_usuario, nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["usina_id"], ["usinas.id"], name="fk_usuarios_usina_id_usinas", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_usuarios"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("ix_usuarios_usina_id", "usuarios", ["usina_id"])

    op.create_table(
        "residuos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("categoria", categoria_residuo, nullable=False),
        sa.Column("percentual_carbono", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("percentual_nitrogenio", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("teor_umidade_percentual", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("percentual_carbono >= 0 AND percentual_carbono <= 100", name="ck_residuos_percentual_carbono_valido"),
        sa.CheckConstraint("percentual_nitrogenio >= 0 AND percentual_nitrogenio <= 100", name="ck_residuos_percentual_nitrogenio_valido"),
        sa.CheckConstraint("teor_umidade_percentual >= 0 AND teor_umidade_percentual <= 100", name="ck_residuos_teor_umidade_valido"),
        sa.PrimaryKeyConstraint("id", name="pk_residuos"),
        sa.UniqueConstraint("nome", name="uq_residuos_nome"),
    )

    op.create_table(
        "leiras",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usina_id", sa.Uuid(), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("data_montagem", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", status_leira, nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("relacao_cn_inicial", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("umidade_inicial_percentual", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("massa_total_kg", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("criado_por_id", sa.Uuid(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["usina_id"], ["usinas.id"], name="fk_leiras_usina_id_usinas", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criado_por_id"], ["usuarios.id"], name="fk_leiras_criado_por_id_usuarios", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_leiras"),
        sa.UniqueConstraint("usina_id", "codigo", name="codigo_unico_por_usina"),
    )
    op.create_index("ix_leiras_usina_id", "leiras", ["usina_id"])

    op.create_table(
        "leira_residuos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("leira_id", sa.Uuid(), nullable=False),
        sa.Column("residuo_id", sa.Uuid(), nullable=False),
        sa.Column("massa_kg", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("massa_kg > 0", name="ck_leira_residuos_massa_positiva"),
        sa.ForeignKeyConstraint(["leira_id"], ["leiras.id"], name="fk_leira_residuos_leira_id_leiras", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["residuo_id"], ["residuos.id"], name="fk_leira_residuos_residuo_id_residuos", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_leira_residuos"),
        sa.UniqueConstraint("leira_id", "residuo_id", name="residuo_unico_por_leira"),
    )
    op.create_index("ix_leira_residuos_leira_id", "leira_residuos", ["leira_id"])
    op.create_index("ix_leira_residuos_residuo_id", "leira_residuos", ["residuo_id"])

    op.create_table(
        "afericoes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("leira_id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("temperatura_celsius", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("umidade_percentual", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("registrado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("id_cliente", sa.Uuid(), nullable=True),
        sa.Column("sincronizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("temperatura_celsius >= -20 AND temperatura_celsius <= 120", name="ck_afericoes_temperatura_em_faixa_plausivel"),
        sa.CheckConstraint("umidade_percentual IS NULL OR (umidade_percentual >= 0 AND umidade_percentual <= 100)", name="ck_afericoes_umidade_valida"),
        sa.ForeignKeyConstraint(["leira_id"], ["leiras.id"], name="fk_afericoes_leira_id_leiras", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], name="fk_afericoes_usuario_id_usuarios", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_afericoes"),
        sa.UniqueConstraint("id_cliente", name="uq_afericoes_id_cliente"),
    )
    op.create_index("ix_afericoes_leira_id", "afericoes", ["leira_id"])
    op.create_index("ix_afericoes_usuario_id", "afericoes", ["usuario_id"])
    op.create_index("ix_afericoes_registrado_em", "afericoes", ["registrado_em"])
    op.create_index("ix_afericoes_leira_registrado", "afericoes", ["leira_id", "registrado_em"])

    op.create_table(
        "alertas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("leira_id", sa.Uuid(), nullable=False),
        sa.Column("afericao_id", sa.Uuid(), nullable=True),
        sa.Column("tipo", tipo_alerta, nullable=False),
        sa.Column("severidade", severidade_alerta, nullable=False),
        sa.Column("status", status_alerta, nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("detectado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reconhecido_por_id", sa.Uuid(), nullable=True),
        sa.Column("reconhecido_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["leira_id"], ["leiras.id"], name="fk_alertas_leira_id_leiras", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["afericao_id"], ["afericoes.id"], name="fk_alertas_afericao_id_afericoes", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reconhecido_por_id"], ["usuarios.id"], name="fk_alertas_reconhecido_por_id_usuarios", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_alertas"),
    )
    op.create_index("ix_alertas_leira_id", "alertas", ["leira_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("acao", acao_auditoria, nullable=False),
        sa.Column("entidade", sa.String(length=50), nullable=False),
        sa.Column("entidade_id", sa.String(length=64), nullable=True),
        sa.Column("dados", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("endereco_ip", sa.String(length=45), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("registrado_em", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], name="fk_audit_log_usuario_id_usuarios", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log"),
    )
    op.create_index("ix_audit_log_usuario_id", "audit_log", ["usuario_id"])
    op.create_index("ix_audit_log_entidade", "audit_log", ["entidade"])
    op.create_index("ix_audit_log_registrado_em", "audit_log", ["registrado_em"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("alertas")
    op.drop_table("afericoes")
    op.drop_table("leira_residuos")
    op.drop_table("leiras")
    op.drop_table("residuos")
    op.drop_table("usuarios")
    op.drop_table("usinas")

    bind = op.get_bind()
    for enum in reversed(_ENUMS):
        enum.drop(bind, checkfirst=True)
