"""Rotas da base de conhecimento de resíduos (exigem autenticação)."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import ResiduoServiceDep, UsuarioAtualDep
from app.application.dto.residuo import ResiduoCriar, ResiduoResponse

router = APIRouter(prefix="/residuos", tags=["Resíduos"])


@router.post("", response_model=ResiduoResponse, status_code=status.HTTP_201_CREATED)
async def criar_residuo(
    dados: ResiduoCriar, servico: ResiduoServiceDep, _: UsuarioAtualDep
) -> ResiduoResponse:
    return await servico.criar(dados)


@router.get("", response_model=list[ResiduoResponse])
async def listar_residuos(
    servico: ResiduoServiceDep,
    _: UsuarioAtualDep,
    limite: int = Query(default=100, ge=1, le=500),
    deslocamento: int = Query(default=0, ge=0),
) -> list[ResiduoResponse]:
    return await servico.listar(limite, deslocamento)


@router.get("/{residuo_id}", response_model=ResiduoResponse)
async def obter_residuo(
    residuo_id: UUID, servico: ResiduoServiceDep, _: UsuarioAtualDep
) -> ResiduoResponse:
    return await servico.obter(residuo_id)
