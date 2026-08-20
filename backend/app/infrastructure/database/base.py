"""Base declarativa do SQLAlchemy, fonte da verdade do schema.

Toda tabela do sistema é definida como uma classe que herda de `Base`. As
migrations do Alembic são geradas a partir de `Base.metadata`, de modo que
alterar um modelo em Python é o que dispara a evolução do banco.

A convenção de nomes garante que índices, constraints e chaves recebam nomes
determinísticos — sem isso, o autogenerate do Alembic produziria migrations
instáveis a cada execução.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

convencao_de_nomes = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convencao_de_nomes)
