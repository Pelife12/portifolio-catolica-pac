"""DTOs da entidade Aferição.

O `usuario_id` NÃO entra no corpo da requisição: é sempre o do usuário
autenticado (RNF01), evitando que alguém registre coleta em nome de outro.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AfericaoCriar(BaseModel):
    leira_id: UUID
    temperatura_celsius: Decimal = Field(ge=-20, le=120)
    umidade_percentual: Decimal | None = Field(default=None, ge=0, le=100)
    # Timestamp real da coleta, gerado no dispositivo (RNF01). Deve trazer fuso.
    registrado_em: datetime
    # Geolocalização obrigatória (RNF01).
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    # UUID gerado no cliente para deduplicar reenvios da sincronização offline.
    id_cliente: UUID | None = None

    @field_validator("registrado_em")
    @classmethod
    def _exige_fuso_horario(cls, valor: datetime) -> datetime:
        if valor.tzinfo is None:
            raise ValueError(
                "registrado_em deve incluir o fuso horário (timestamp com timezone)."
            )
        return valor


class AfericaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leira_id: UUID
    usuario_id: UUID
    temperatura_celsius: Decimal
    umidade_percentual: Decimal | None
    registrado_em: datetime
    latitude: Decimal
    longitude: Decimal
    id_cliente: UUID | None
    sincronizado_em: datetime
