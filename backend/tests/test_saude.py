"""Testes do endpoint de health-check."""


async def test_retorna_operacional_quando_banco_responde(client):
    resposta = await client.get("/api/v1/saude")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "operacional"
    assert corpo["api"] == "operacional"
    assert corpo["banco_de_dados"] == "operacional"
    assert corpo["versao"]


async def test_retorna_503_quando_banco_esta_fora(client, verificador_fake):
    verificador_fake.disponivel = False

    resposta = await client.get("/api/v1/saude")

    assert resposta.status_code == 503
    corpo = resposta.json()
    assert corpo["status"] == "degradado"
    assert corpo["banco_de_dados"] == "indisponivel"
