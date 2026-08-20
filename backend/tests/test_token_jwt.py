"""Testes do gerador de token JWT (ida e volta e validações)."""

import uuid

import pytest

from app.domain.exceptions import NaoAutenticado
from app.infrastructure.security.token_jwt import GeradorDeTokenJWT


def _gerador(expira_minutos: int = 60) -> GeradorDeTokenJWT:
    return GeradorDeTokenJWT(
        segredo="segredo-de-teste", algoritmo="HS256", expira_minutos=expira_minutos
    )


def test_token_gerado_e_decodificado_preserva_dados():
    gerador = _gerador()
    usuario_id = uuid.uuid4()

    token = gerador.gerar_token_de_acesso(usuario_id, "operador")
    dados = gerador.decodificar(token)

    assert dados.usuario_id == usuario_id
    assert dados.papel == "operador"


def test_expira_em_segundos_reflete_configuracao():
    assert _gerador(expira_minutos=8).expira_em_segundos == 480


def test_token_invalido_e_rejeitado():
    with pytest.raises(NaoAutenticado):
        _gerador().decodificar("isto-nao-e-um-token")


def test_token_assinado_com_outro_segredo_e_rejeitado():
    emissor = GeradorDeTokenJWT("segredo-A", "HS256", 60)
    verificador = GeradorDeTokenJWT("segredo-B", "HS256", 60)

    token = emissor.gerar_token_de_acesso(uuid.uuid4(), "gestor")

    with pytest.raises(NaoAutenticado):
        verificador.decodificar(token)
