"""Testes da tradução de erros do banco para respostas HTTP (hardening de 26/11)."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import IntegrityError, OperationalError

from app.main import criar_app


class ErroOriginal(Exception):
    """Imita a exceção do driver, que carrega o SQLSTATE do PostgreSQL."""

    def __init__(self, mensagem: str, sqlstate: str | None) -> None:
        super().__init__(mensagem)
        self.sqlstate = sqlstate


def _app_que_levanta(exc: Exception):
    app = criar_app()

    @app.get("/teste/erro")
    async def levantar():
        raise exc

    return app


async def _requisitar(exc: Exception):
    app = _app_que_levanta(exc)
    # raise_app_exceptions=False: o handler de Exception responde como em produção.
    transporte = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transporte, base_url="http://t") as cliente:
        return await cliente.get("/teste/erro")


async def test_gatilho_da_trava_de_24h_vira_422_igual_a_validacao_da_api():
    resposta = await _requisitar(
        IntegrityError(
            "INSERT INTO afericoes ...",
            {},
            ErroOriginal("Afericao com data retroativa a mais de 24 horas nao e permitida", "23514"),
        )
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "AfericaoForaDaJanela"


@pytest.mark.parametrize(
    ("sqlstate", "status_esperado", "erro_esperado"),
    [
        ("23514", 422, "RegraDeNegocioViolada"),
        ("23505", 409, "EntidadeDuplicada"),
        ("23503", 422, "RegraDeNegocioViolada"),
    ],
)
async def test_violacoes_de_integridade(sqlstate, status_esperado, erro_esperado):
    resposta = await _requisitar(IntegrityError("SQL", {}, ErroOriginal("violação", sqlstate)))

    assert resposta.status_code == status_esperado
    assert resposta.json()["erro"] == erro_esperado


async def test_banco_fora_do_ar_vira_503():
    resposta = await _requisitar(
        OperationalError("SELECT 1", {}, ErroOriginal("connection refused", None))
    )

    assert resposta.status_code == 503
    assert resposta.json()["erro"] == "ServicoIndisponivel"


async def test_erro_inesperado_nao_vaza_detalhe_interno():
    resposta = await _requisitar(RuntimeError("segredo interno: senha=123"))

    assert resposta.status_code == 500
    corpo = resposta.json()
    assert corpo["erro"] == "ErroInterno"
    assert "senha" not in corpo["mensagem"]
