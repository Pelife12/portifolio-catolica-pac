"""DTOs da entidade Leira.

O cálculo de traço (relação C/N e umidade a partir da composição) é a entrega
de 27/08 (RF01); aqui a leira é criada com seus dados de identificação e ciclo.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.database.models.enums import StatusLeira


class LeiraCriar(BaseModel):
    usina_id: UUID
    codigo: str = Field(min_length=1, max_length=50)
    data_montagem: datetime
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacoes: str | None = None


class LeiraAtualizar(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)
    status: StatusLeira | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacoes: str | None = None


class LeiraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usina_id: UUID
    codigo: str
    data_montagem: datetime
    status: StatusLeira
    latitude: Decimal | None
    longitude: Decimal | None
    relacao_cn_inicial: Decimal | None
    umidade_inicial_percentual: Decimal | None
    massa_total_kg: Decimal | None
    observacoes: str | None
    criado_por_id: UUID | None
    criado_em: datetime
    atualizado_em: datetime
