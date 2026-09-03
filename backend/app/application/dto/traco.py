"""DTOs do cálculo de traço (RF01)."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ItemComposicao(BaseModel):
    """Um resíduo e sua massa na mistura."""

    residuo_id: UUID
    massa_kg: Decimal = Field(gt=0, description="Massa úmida do resíduo, em kg.")


class ComposicaoRequest(BaseModel):
    itens: list[ItemComposicao] = Field(min_length=1)


class ResultadoTracoResponse(BaseModel):
    massa_total_kg: Decimal
    massa_seca_kg: Decimal
    carbono_total_kg: Decimal
    nitrogenio_total_kg: Decimal
    relacao_cn: Decimal
    umidade_percentual: Decimal
    cn_dentro_do_ideal: bool
    umidade_dentro_do_ideal: bool


class ComposicaoItemResponse(BaseModel):
    """Um item da composição salva de uma leira."""

    residuo_id: UUID
    residuo_nome: str
    massa_kg: Decimal
