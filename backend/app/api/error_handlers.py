"""Tradução das exceções de domínio para respostas HTTP."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    ErroDeDominio,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,
    ServicoIndisponivel,
)

_STATUS_POR_EXCECAO: dict[type[ErroDeDominio], int] = {
    RecursoNaoEncontrado: status.HTTP_404_NOT_FOUND,
    RegraDeNegocioViolada: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ServicoIndisponivel: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def registrar_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroDeDominio)
    async def tratar_erro_de_dominio(_: Request, exc: ErroDeDominio) -> JSONResponse:
        codigo = _STATUS_POR_EXCECAO.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=codigo,
            content={"erro": type(exc).__name__, "mensagem": exc.mensagem},
        )
