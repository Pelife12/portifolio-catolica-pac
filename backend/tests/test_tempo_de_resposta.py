"""Testes do medidor de tempo de resposta (RNF02)."""

import logging

from httpx import ASGITransport, AsyncClient

from app.api.deps import get_verificador_de_saude
from app.api.middlewares import registrar_medidor_de_tempo
from app.main import criar_app
from tests.conftest import VerificadorDeSaudeFake


async def test_toda_resposta_carrega_server_timing(client):
    resposta = await client.get("/api/v1/saude")

    assert resposta.headers["server-timing"].startswith("app;dur=")


async def test_registra_aviso_quando_o_teto_e_ultrapassado(caplog):
    app = criar_app()
    # Teto negativo: qualquer requisição fica acima dele.
    registrar_medidor_de_tempo(app, teto_ms=-1)
    app.dependency_overrides[get_verificador_de_saude] = lambda: VerificadorDeSaudeFake()

    with caplog.at_level(logging.WARNING, logger="app.desempenho"):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as ac:
            await ac.get("/api/v1/saude")

    assert any("RNF02" in registro.message for registro in caplog.records)
