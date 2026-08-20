"""Rotas de CRUD de Leiras (todas exigem autenticação)."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import LeiraServiceDep, UsuarioAtualDep
from app.application.dto.leira import LeiraAtualizar, LeiraCriar, LeiraResponse

router = APIRouter(prefix="/leiras", tags=["Leiras"])


@router.post("", response_model=LeiraResponse, status_code=status.HTTP_201_CREATED)
async def criar_leira(
    dados: LeiraCriar, servico: LeiraServiceDep, usuario_atual: UsuarioAtualDep
) -> LeiraResponse:
    # Registra quem criou a leira para a trilha de auditoria.
    return await servico.criar(dados, criado_por_id=usuario_atual.id)


@router.get("", response_model=list[LeiraResponse])
async def listar_leiras(
    servico: LeiraServiceDep,
    _: UsuarioAtualDep,
    usina_id: UUID | None = Query(default=None),
    limite: int = Query(default=50, ge=1, le=200),
    deslocamento: int = Query(default=0, ge=0),
) -> list[LeiraResponse]:
    return await servico.listar(usina_id, limite, deslocamento)


@router.get("/{leira_id}", response_model=LeiraResponse)
async def obter_leira(
    leira_id: UUID, servico: LeiraServiceDep, _: UsuarioAtualDep
) -> LeiraResponse:
    return await servico.obter(leira_id)


@router.patch("/{leira_id}", response_model=LeiraResponse)
async def atualizar_leira(
    leira_id: UUID, dados: LeiraAtualizar, servico: LeiraServiceDep, _: UsuarioAtualDep
) -> LeiraResponse:
    return await servico.atualizar(leira_id, dados)


@router.delete("/{leira_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_leira(
    leira_id: UUID, servico: LeiraServiceDep, _: UsuarioAtualDep
) -> None:
    await servico.remover(leira_id)
