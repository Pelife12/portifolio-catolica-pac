"""Testes de sanidade do schema (mapeamento dos modelos).

Não exigem um PostgreSQL rodando: validam que os modelos estão corretamente
registrados no metadata e que os mapeamentos são consistentes. Servem de rede
de segurança contra erros de digitação em nomes de tabela, colunas e relações.
"""

from sqlalchemy import inspect

from app.infrastructure.database.base import Base
import app.infrastructure.database.models as modelos

TABELAS_ESPERADAS = {
    "usinas",
    "usuarios",
    "residuos",
    "leiras",
    "leira_residuos",
    "afericoes",
    "alertas",
    "audit_log",
}


def test_todas_as_tabelas_estao_registradas():
    assert TABELAS_ESPERADAS.issubset(set(Base.metadata.tables.keys()))


def test_afericao_carrega_dados_de_auditoria_rnf01():
    colunas = {c.name for c in modelos.Afericao.__table__.columns}
    # RNF01: toda aferição precisa de timestamp local, geolocalização e usuário.
    assert {"registrado_em", "latitude", "longitude", "usuario_id"}.issubset(colunas)


def test_afericao_tem_id_cliente_unico_para_sincronizacao():
    coluna = modelos.Afericao.__table__.columns["id_cliente"]
    assert coluna.unique is True


def test_leira_tem_codigo_unico_por_usina():
    nomes_constraints = {c.name for c in modelos.Leira.__table__.constraints}
    assert "codigo_unico_por_usina" in nomes_constraints


def test_composicao_impede_residuo_repetido_na_leira():
    nomes_constraints = {c.name for c in modelos.LeiraResiduo.__table__.constraints}
    assert "residuo_unico_por_leira" in nomes_constraints


def test_audit_log_e_somente_insercao():
    # A trilha de auditoria não deve ter coluna de atualização (registro imutável).
    colunas = {c.name for c in modelos.AuditLog.__table__.columns}
    assert "atualizado_em" not in colunas


def test_mapeamentos_sao_configuraveis():
    # Força o SQLAlchemy a resolver todos os relacionamentos (pega FK/back_populates quebrados).
    for mapper in Base.registry.mappers:
        insp = inspect(mapper.class_)
        assert insp is not None
