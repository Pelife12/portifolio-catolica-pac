"""Tradução das exceções de domínio para respostas HTTP."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AcessoNegado,
    CredenciaisInvalidas,
    EntidadeDuplicada,
    ErroDeDominio,
    NaoAutenticado,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,
    ServicoIndisponivel,
)

# Mapeamento das exceções mais específicas primeiro: a resolução percorre a MRO
# da exceção, então subclasses caem no ancestral conhecido mais próximo.
_STATUS_POR_EXCECAO: dict[type[ErroDeDominio], int] = {
    CredenciaisInvalidas: status.HTTP_401_UNAUTHORIZED,
    NaoAutenticado: status.HTTP_401_UNAUTHORIZED,
    AcessoNegado: status.HTTP_403_FORBIDDEN,
    RecursoNaoEncontrado: status.HTTP_404_NOT_FOUND,
    EntidadeDuplicada: status.HTTP_409_CONFLICT,
    RegraDeNegocioViolada: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ServicoIndisponivel: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def _resolver_status(exc: ErroDeDominio) -> int:
    for classe in type(exc).__mro__:
        if classe in _STATUS_POR_EXCECAO:
            return _STATUS_POR_EXCECAO[classe]
    return status.HTTP_400_BAD_REQUEST


def registrar_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroDeDominio)
    async def tratar_erro_de_dominio(_: Request, exc: ErroDeDominio) -> JSONResponse:
        codigo = _resolver_status(exc)
        cabecalhos = (
            {"WWW-Authenticate": "Bearer"}
            if codigo == status.HTTP_401_UNAUTHORIZED
            else None
        )
        return JSONResponse(
            status_code=codigo,
            content={"erro": type(exc).__name__, "mensagem": exc.mensagem},
            headers=cabecalhos,
        )
