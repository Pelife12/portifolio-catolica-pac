"""Rotas de CRUD de Usinas (todas exigem autenticação)."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import UsinaServiceDep, UsuarioAtualDep
from app.application.dto.usina import UsinaAtualizar, UsinaCriar, UsinaResponse

router = APIRouter(prefix="/usinas", tags=["Usinas"])


@router.post("", response_model=UsinaResponse, status_code=status.HTTP_201_CREATED)
async def criar_usina(
    dados: UsinaCriar, servico: UsinaServiceDep, _: UsuarioAtualDep
) -> UsinaResponse:
    return await servico.criar(dados)


@router.get("", response_model=list[UsinaResponse])
async def listar_usinas(
    servico: UsinaServiceDep,
    _: UsuarioAtualDep,
    limite: int = Query(default=50, ge=1, le=200),
    deslocamento: int = Query(default=0, ge=0),
) -> list[UsinaResponse]:
    return await servico.listar(limite, deslocamento)


@router.get("/{usina_id}", response_model=UsinaResponse)
async def obter_usina(
    usina_id: UUID, servico: UsinaServiceDep, _: UsuarioAtualDep
) -> UsinaResponse:
    return await servico.obter(usina_id)


@router.patch("/{usina_id}", response_model=UsinaResponse)
async def atualizar_usina(
    usina_id: UUID, dados: UsinaAtualizar, servico: UsinaServiceDep, _: UsuarioAtualDep
) -> UsinaResponse:
    return await servico.atualizar(usina_id, dados)


@router.delete("/{usina_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_usina(
    usina_id: UUID, servico: UsinaServiceDep, _: UsuarioAtualDep
) -> None:
    await servico.remover(usina_id)
