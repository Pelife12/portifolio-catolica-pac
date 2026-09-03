"""DTOs da entidade Resíduo (base de conhecimento do traço)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.database.models.enums import CategoriaResiduo

_PCT = {"ge": 0, "le": 100}


class ResiduoCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    categoria: CategoriaResiduo
    percentual_carbono: Decimal = Field(**_PCT)
    percentual_nitrogenio: Decimal = Field(**_PCT)
    teor_umidade_percentual: Decimal = Field(**_PCT)


class ResiduoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    categoria: CategoriaResiduo
    percentual_carbono: Decimal
    percentual_nitrogenio: Decimal
    teor_umidade_percentual: Decimal
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
