"""Resíduo compostável: catálogo agronômico (base de conhecimento do traço).

Cada resíduo carrega os parâmetros necessários para o cálculo de traço (RF01):
o percentual de carbono e de nitrogênio (base seca) e o teor de umidade. A
partir das massas informadas na montagem da leira, o motor calcula a relação
C/N e a umidade resultantes da mistura.
"""

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import CategoriaResiduo
from app.infrastructure.database.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Residuo(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "residuos"

    nome: Mapped[str] = mapped_column(sa.String(150), nullable=False, unique=True)
    categoria: Mapped[CategoriaResiduo] = mapped_column(
        sa.Enum(CategoriaResiduo, name="categoria_residuo", create_type=False),
        nullable=False,
    )
    # Percentuais em base seca; usados no balanço de Carbono/Nitrogênio.
    percentual_carbono: Mapped[float] = mapped_column(sa.Numeric(5, 2), nullable=False)
    percentual_nitrogenio: Mapped[float] = mapped_column(sa.Numeric(5, 2), nullable=False)
    # Umidade típica do resíduo (% da massa úmida).
    teor_umidade_percentual: Mapped[float] = mapped_column(sa.Numeric(5, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    __table_args__ = (
        sa.CheckConstraint(
            "percentual_carbono >= 0 AND percentual_carbono <= 100",
            name="percentual_carbono_valido",
        ),
        sa.CheckConstraint(
            "percentual_nitrogenio >= 0 AND percentual_nitrogenio <= 100",
            name="percentual_nitrogenio_valido",
        ),
        sa.CheckConstraint(
            "teor_umidade_percentual >= 0 AND teor_umidade_percentual <= 100",
            name="teor_umidade_valido",
        ),
    )
