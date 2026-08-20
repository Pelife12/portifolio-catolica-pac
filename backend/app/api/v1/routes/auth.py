"""Rotas de autenticação."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AutenticacaoServiceDep, UsuarioAtualDep
from app.application.dto.autenticacao import TokenResponse
from app.application.dto.usuario import UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse, summary="Autentica e emite o token")
async def login(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
    servico: AutenticacaoServiceDep,
) -> TokenResponse:
    # O campo padrão do formulário OAuth2 chama-se "username"; aqui é o e-mail.
    return await servico.autenticar(formulario.username, formulario.password)


@router.get("/eu", response_model=UsuarioResponse, summary="Dados do usuário autenticado")
async def usuario_autenticado(usuario_atual: UsuarioAtualDep) -> UsuarioResponse:
    return UsuarioResponse.model_validate(usuario_atual)
