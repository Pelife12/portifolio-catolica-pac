"""Rotas de alertas e da avaliação da leira pelo motor (RF03)."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import AlertaServiceDep, MotorServiceDep, UsuarioAtualDep
from app.application.dto.alerta import AlertaResponse
from app.infrastructure.database.models.enums import StatusAlerta

router = APIRouter(tags=["Alertas"])


@router.post("/leiras/{leira_id}/avaliar", response_model=list[AlertaResponse])
async def avaliar_leira(
    leira_id: UUID, servico: MotorServiceDep, _: UsuarioAtualDep
) -> list[AlertaResponse]:
    """Roda o motor termofílico e retorna os alertas recém-gerados (se houver)."""
    return await servico.avaliar_leira(leira_id)


@router.get("/alertas", response_model=list[AlertaResponse])
async def listar_alertas(
    servico: AlertaServiceDep,
    _: UsuarioAtualDep,
    leira_id: UUID | None = Query(default=None),
    status: StatusAlerta | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    deslocamento: int = Query(default=0, ge=0),
) -> list[AlertaResponse]:
    return await servico.listar(leira_id, status, limite, deslocamento)


@router.get("/alertas/{alerta_id}", response_model=AlertaResponse)
async def obter_alerta(
    alerta_id: UUID, servico: AlertaServiceDep, _: UsuarioAtualDep
) -> AlertaResponse:
    return await servico.obter(alerta_id)


@router.post("/alertas/{alerta_id}/reconhecer", response_model=AlertaResponse)
async def reconhecer_alerta(
    alerta_id: UUID, servico: AlertaServiceDep, usuario_atual: UsuarioAtualDep
) -> AlertaResponse:
    return await servico.reconhecer(alerta_id, usuario_id=usuario_atual.id)


@router.post("/alertas/{alerta_id}/resolver", response_model=AlertaResponse)
async def resolver_alerta(
    alerta_id: UUID, servico: AlertaServiceDep, _: UsuarioAtualDep
) -> AlertaResponse:
    return await servico.resolver(alerta_id)
