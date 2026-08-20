"""Rotas de CRUD de Usuários (todas exigem autenticação)."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import UsuarioAtualDep, UsuarioServiceDep
from app.application.dto.usuario import UsuarioAtualizar, UsuarioCriar, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    dados: UsuarioCriar, servico: UsuarioServiceDep, _: UsuarioAtualDep
) -> UsuarioResponse:
    return await servico.criar(dados)


@router.get("", response_model=list[UsuarioResponse])
async def listar_usuarios(
    servico: UsuarioServiceDep,
    _: UsuarioAtualDep,
    usina_id: UUID | None = Query(default=None),
    limite: int = Query(default=50, ge=1, le=200),
    deslocamento: int = Query(default=0, ge=0),
) -> list[UsuarioResponse]:
    return await servico.listar(usina_id, limite, deslocamento)


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obter_usuario(
    usuario_id: UUID, servico: UsuarioServiceDep, _: UsuarioAtualDep
) -> UsuarioResponse:
    return await servico.obter(usuario_id)


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    usuario_id: UUID,
    dados: UsuarioAtualizar,
    servico: UsuarioServiceDep,
    _: UsuarioAtualDep,
) -> UsuarioResponse:
    return await servico.atualizar(usuario_id, dados)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_usuario(
    usuario_id: UUID, servico: UsuarioServiceDep, _: UsuarioAtualDep
) -> None:
    await servico.remover(usuario_id)
