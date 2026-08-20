"""DTOs da entidade Usina."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UsinaCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=150)
    cnpj: str | None = Field(default=None, max_length=14)
    endereco: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class UsinaAtualizar(BaseModel):
    """Todos os campos opcionais: atualização parcial (PATCH)."""

    nome: str | None = Field(default=None, min_length=1, max_length=150)
    cnpj: str | None = Field(default=None, max_length=14)
    endereco: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    ativa: bool | None = None


class UsinaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    cnpj: str | None
    endereco: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    ativa: bool
    criado_em: datetime
    atualizado_em: datetime
