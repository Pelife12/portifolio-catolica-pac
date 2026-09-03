"""Composition root: aqui as dependências concretas são injetadas nos casos de uso.

Este é o único ponto onde a camada de API conhece a infraestrutura. Os serviços
e casos de uso continuam recebendo apenas abstrações (ports).
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import (
    AfericaoRepository,
    LeiraRepository,
    LeiraResiduoRepository,
    ResiduoRepository,
    UsinaRepository,
    UsuarioRepository,
)
from app.application.ports.seguranca import GeradorDeToken, HashDeSenha
from app.application.services.afericao_service import AfericaoService
from app.application.services.autenticacao_service import AutenticacaoService
from app.application.services.leira_service import LeiraService
from app.application.services.residuo_service import ResiduoService
from app.application.services.traco_service import TracoService
from app.application.services.usina_service import UsinaService
from app.application.services.usuario_service import UsuarioService
from app.application.use_cases.verificar_saude import VerificarSaudeUseCase
from app.domain.exceptions import AcessoNegado, NaoAutenticado
from app.domain.repositories.verificador_de_saude import VerificadorDeSaudeDoBanco
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.models.usuario import Usuario
from app.infrastructure.database.session import get_session
from app.infrastructure.database.verificador_de_saude_postgres import (
    VerificadorDeSaudePostgres,
)
from app.infrastructure.repositories.afericao_repository_sqlalchemy import (
    AfericaoRepositorySQLAlchemy,
)
from app.infrastructure.repositories.leira_repository_sqlalchemy import (
    LeiraRepositorySQLAlchemy,
)
from app.infrastructure.repositories.leira_residuo_repository_sqlalchemy import (
    LeiraResiduoRepositorySQLAlchemy,
)
from app.infrastructure.repositories.residuo_repository_sqlalchemy import (
    ResiduoRepositorySQLAlchemy,
)
from app.infrastructure.repositories.usina_repository_sqlalchemy import (
    UsinaRepositorySQLAlchemy,
)
from app.infrastructure.repositories.usuario_repository_sqlalchemy import (
    UsuarioRepositorySQLAlchemy,
)
from app.infrastructure.security.hash_bcrypt import HashDeSenhaBcrypt
from app.infrastructure.security.token_jwt import GeradorDeTokenJWT

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Token endpoint usado pelo Swagger para o botão "Authorize".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


# ---------------------------------------------------------------------------
# Saúde
# ---------------------------------------------------------------------------
def get_verificador_de_saude(session: SessionDep) -> VerificadorDeSaudeDoBanco:
    return VerificadorDeSaudePostgres(session)


def get_verificar_saude_use_case(
    verificador: Annotated[VerificadorDeSaudeDoBanco, Depends(get_verificador_de_saude)],
) -> VerificarSaudeUseCase:
    return VerificarSaudeUseCase(verificador)


VerificarSaudeUseCaseDep = Annotated[
    VerificarSaudeUseCase, Depends(get_verificar_saude_use_case)
]


# ---------------------------------------------------------------------------
# Segurança (hash e token são sem estado; cacheados por processo)
# ---------------------------------------------------------------------------
@lru_cache
def get_hash_de_senha() -> HashDeSenha:
    return HashDeSenhaBcrypt()


@lru_cache
def get_gerador_de_token() -> GeradorDeToken:
    settings = get_settings()
    return GeradorDeTokenJWT(
        segredo=settings.jwt_segredo,
        algoritmo=settings.jwt_algoritmo,
        expira_minutos=settings.jwt_expira_minutos,
    )


HashDep = Annotated[HashDeSenha, Depends(get_hash_de_senha)]
TokenGenDep = Annotated[GeradorDeToken, Depends(get_gerador_de_token)]


# ---------------------------------------------------------------------------
# Repositórios (um por requisição, ligados à sessão)
# ---------------------------------------------------------------------------
def get_usina_repo(session: SessionDep) -> UsinaRepository:
    return UsinaRepositorySQLAlchemy(session)


def get_usuario_repo(session: SessionDep) -> UsuarioRepository:
    return UsuarioRepositorySQLAlchemy(session)


def get_leira_repo(session: SessionDep) -> LeiraRepository:
    return LeiraRepositorySQLAlchemy(session)


def get_residuo_repo(session: SessionDep) -> ResiduoRepository:
    return ResiduoRepositorySQLAlchemy(session)


def get_leira_residuo_repo(session: SessionDep) -> LeiraResiduoRepository:
    return LeiraResiduoRepositorySQLAlchemy(session)


def get_afericao_repo(session: SessionDep) -> AfericaoRepository:
    return AfericaoRepositorySQLAlchemy(session)


UsinaRepoDep = Annotated[UsinaRepository, Depends(get_usina_repo)]
UsuarioRepoDep = Annotated[UsuarioRepository, Depends(get_usuario_repo)]
LeiraRepoDep = Annotated[LeiraRepository, Depends(get_leira_repo)]
ResiduoRepoDep = Annotated[ResiduoRepository, Depends(get_residuo_repo)]
LeiraResiduoRepoDep = Annotated[LeiraResiduoRepository, Depends(get_leira_residuo_repo)]
AfericaoRepoDep = Annotated[AfericaoRepository, Depends(get_afericao_repo)]


# ---------------------------------------------------------------------------
# Serviços de aplicação
# ---------------------------------------------------------------------------
def get_autenticacao_service(
    usuario_repo: UsuarioRepoDep, hash_senha: HashDep, gerador: TokenGenDep
) -> AutenticacaoService:
    return AutenticacaoService(usuario_repo, hash_senha, gerador)


def get_usina_service(usina_repo: UsinaRepoDep) -> UsinaService:
    return UsinaService(usina_repo)


def get_usuario_service(
    usuario_repo: UsuarioRepoDep, usina_repo: UsinaRepoDep, hash_senha: HashDep
) -> UsuarioService:
    return UsuarioService(usuario_repo, usina_repo, hash_senha)


def get_leira_service(leira_repo: LeiraRepoDep, usina_repo: UsinaRepoDep) -> LeiraService:
    return LeiraService(leira_repo, usina_repo)


def get_residuo_service(residuo_repo: ResiduoRepoDep) -> ResiduoService:
    return ResiduoService(residuo_repo)


def get_traco_service(
    residuo_repo: ResiduoRepoDep,
    leira_repo: LeiraRepoDep,
    leira_residuo_repo: LeiraResiduoRepoDep,
) -> TracoService:
    return TracoService(residuo_repo, leira_repo, leira_residuo_repo)


def get_afericao_service(
    afericao_repo: AfericaoRepoDep, leira_repo: LeiraRepoDep, settings: SettingsDep
) -> AfericaoService:
    return AfericaoService(
        afericao_repo, leira_repo, settings.janela_retroativa_horas
    )


AutenticacaoServiceDep = Annotated[AutenticacaoService, Depends(get_autenticacao_service)]
UsinaServiceDep = Annotated[UsinaService, Depends(get_usina_service)]
UsuarioServiceDep = Annotated[UsuarioService, Depends(get_usuario_service)]
LeiraServiceDep = Annotated[LeiraService, Depends(get_leira_service)]
ResiduoServiceDep = Annotated[ResiduoService, Depends(get_residuo_service)]
TracoServiceDep = Annotated[TracoService, Depends(get_traco_service)]
AfericaoServiceDep = Annotated[AfericaoService, Depends(get_afericao_service)]


# ---------------------------------------------------------------------------
# Usuário autenticado
# ---------------------------------------------------------------------------
async def get_usuario_atual(
    token: TokenDep, gerador: TokenGenDep, usuario_repo: UsuarioRepoDep
) -> Usuario:
    """Valida o token e carrega o usuário correspondente (recurso protegido)."""
    dados = gerador.decodificar(token)
    usuario = await usuario_repo.obter_por_id(dados.usuario_id)
    if usuario is None:
        raise NaoAutenticado("Usuário do token não existe mais.")
    if not usuario.ativo:
        raise AcessoNegado("Usuário inativo.")
    return usuario


UsuarioAtualDep = Annotated[Usuario, Depends(get_usuario_atual)]
