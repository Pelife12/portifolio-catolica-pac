"""Base declarativa do SQLAlchemy.

As tabelas do sistema (usinas, leiras, aferições, alertas, audit_log) serão
mapeadas sobre esta base na entrega de 13/08.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
