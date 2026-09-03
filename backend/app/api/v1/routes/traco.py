"""Rotas do cálculo de traço (RF01).

- POST /calculos/traco: cálculo avulso (preview), sem persistir — pensado para o
  cálculo em tempo real na tela de cadastro da leira no PWA.
- PUT/GET /leiras/{id}/composicao: define e consulta a composição de uma leira,
  gravando o traço inicial no cadastro.
"""

from uuid import UUID

from fastapi import APIRouter

from app.api.deps import TracoServiceDep, UsuarioAtualDep
from app.application.dto.leira import LeiraResponse
from app.application.dto.traco import (
    ComposicaoItemResponse,
    ComposicaoRequest,
    ResultadoTracoResponse,
)

router = APIRouter(tags=["Traço"])


@router.post("/calculos/traco", response_model=ResultadoTracoResponse)
async def calcular_traco(
    dados: ComposicaoRequest, servico: TracoServiceDep, _: UsuarioAtualDep
) -> ResultadoTracoResponse:
    return await servico.calcular(dados.itens)


@router.put("/leiras/{leira_id}/composicao", response_model=LeiraResponse)
async def definir_composicao(
    leira_id: UUID,
    dados: ComposicaoRequest,
    servico: TracoServiceDep,
    _: UsuarioAtualDep,
) -> LeiraResponse:
    return await servico.definir_composicao(leira_id, dados.itens)


@router.get(
    "/leiras/{leira_id}/composicao", response_model=list[ComposicaoItemResponse]
)
async def listar_composicao(
    leira_id: UUID, servico: TracoServiceDep, _: UsuarioAtualDep
) -> list[ComposicaoItemResponse]:
    return await servico.listar_composicao(leira_id)
