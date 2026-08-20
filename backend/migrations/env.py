"""Ambiente de execução das migrations do Alembic.

Liga o Alembic à fonte da verdade do schema:

* a URL do banco vem do `Settings` da aplicação (variável DATABASE_URL);
* o `target_metadata` é o `Base.metadata`, populado ao importar o pacote de
  modelos.

Com isso, `alembic revision --autogenerate` compara os modelos Python com o
banco e escreve a migration correspondente — alterar um modelo passa a ser o
gatilho para evoluir o banco.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.pool import NullPool

from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.base import Base

# Importar o pacote de modelos registra todas as tabelas em Base.metadata.
import app.infrastructure.database.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Injeta a URL da aplicação na config do Alembic (asyncpg é async).
config.set_main_option("sqlalchemy.url", str(get_settings().database_url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL sem conectar ao banco (modo --sql)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Detecta mudança de tipo e de default ao autogerar, não só de colunas.
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Conecta com engine assíncrona (asyncpg) e aplica as migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
