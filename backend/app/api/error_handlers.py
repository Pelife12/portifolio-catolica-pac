"""Tradução das exceções para respostas HTTP.

Toda resposta de erro da API tem o mesmo corpo — `{"erro": ..., "mensagem": ...}`
—, seja a falha uma regra de negócio, uma recusa do próprio banco (o gatilho da
trava de 24h, uma unique) ou um erro inesperado. O PWA depende disso para
decidir se uma coleta da fila é recusada de vez ou se vale tentar de novo.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError

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

logger = logging.getLogger(__name__)

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

# Códigos SQLSTATE do PostgreSQL tratados como erro do cliente.
_SQLSTATE_CHECK = "23514"
_SQLSTATE_UNIQUE = "23505"
_SQLSTATE_CHAVE_ESTRANGEIRA = "23503"
_PREFIXO_FALHA_DE_CONEXAO = "08"

# Texto levantado por fn_afericao_trava_temporal (migration 0002).
_MARCA_DA_TRAVA_TEMPORAL = "Afericao com data"


def _resolver_status(exc: ErroDeDominio) -> int:
    for classe in type(exc).__mro__:
        if classe in _STATUS_POR_EXCECAO:
            return _STATUS_POR_EXCECAO[classe]
    return status.HTTP_400_BAD_REQUEST


def _corpo(codigo: int, erro: str, mensagem: str, cabecalhos=None) -> JSONResponse:
    return JSONResponse(
        status_code=codigo, content={"erro": erro, "mensagem": mensagem}, headers=cabecalhos
    )


def _sqlstate(exc: DBAPIError) -> str | None:
    """SQLSTATE do erro original; o asyncpg o expõe na exceção encadeada."""
    origem = exc.orig
    for candidato in (origem, getattr(origem, "__cause__", None)):
        codigo = getattr(candidato, "sqlstate", None) or getattr(candidato, "pgcode", None)
        if codigo:
            return str(codigo)
    return None


def registrar_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErroDeDominio)
    async def tratar_erro_de_dominio(_: Request, exc: ErroDeDominio) -> JSONResponse:
        codigo = _resolver_status(exc)
        cabecalhos = (
            {"WWW-Authenticate": "Bearer"} if codigo == status.HTTP_401_UNAUTHORIZED else None
        )
        return _corpo(codigo, type(exc).__name__, exc.mensagem, cabecalhos)

    @app.exception_handler(DBAPIError)
    async def tratar_erro_do_banco(requisicao: Request, exc: DBAPIError) -> JSONResponse:
        sqlstate = _sqlstate(exc)
        texto = str(exc.orig)

        if sqlstate == _SQLSTATE_CHECK and _MARCA_DA_TRAVA_TEMPORAL in texto:
            # O gatilho do banco é a última linha da trava de 24h (RF02): mesma
            # resposta da validação da API, para o PWA tratar igual.
            return _corpo(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "AfericaoForaDaJanela",
                "Coleta recusada pelo banco: horário retroativo a mais de 24 horas ou no futuro.",
            )
        if sqlstate == _SQLSTATE_CHECK:
            return _corpo(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "RegraDeNegocioViolada",
                "Algum valor está fora da faixa permitida.",
            )
        if sqlstate == _SQLSTATE_UNIQUE:
            return _corpo(
                status.HTTP_409_CONFLICT, "EntidadeDuplicada", "Já existe um registro com esses dados."
            )
        if sqlstate == _SQLSTATE_CHAVE_ESTRANGEIRA:
            return _corpo(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "RegraDeNegocioViolada",
                "O registro relacionado não existe ou ainda está em uso.",
            )
        if isinstance(exc, (OperationalError, InterfaceError)) or (
            sqlstate or ""
        ).startswith(_PREFIXO_FALHA_DE_CONEXAO):
            logger.error("Banco indisponível em %s: %s", requisicao.url.path, texto)
            return _corpo(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "ServicoIndisponivel",
                "Banco de dados temporariamente indisponível.",
            )

        logger.exception("Erro de banco não previsto em %s", requisicao.url.path)
        return _corpo(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "ErroInterno", "Erro interno ao acessar os dados."
        )

    @app.exception_handler(Exception)
    async def tratar_erro_inesperado(requisicao: Request, exc: Exception) -> JSONResponse:
        # Nunca devolve detalhe interno (stack, SQL) para o cliente; fica no log.
        logger.exception("Erro não tratado em %s %s", requisicao.method, requisicao.url.path)
        return _corpo(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "ErroInterno",
            "Erro interno. A equipe foi notificada pelo log do servidor.",
        )
