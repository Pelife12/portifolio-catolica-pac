"""Testes do serviço de autenticação, com dublês dos ports (sem banco)."""

import uuid

import pytest

from app.application.ports.repositorios import UsuarioRepository
from app.application.ports.seguranca import DadosDoToken, GeradorDeToken, HashDeSenha
from app.application.services.autenticacao_service import AutenticacaoService
from app.domain.exceptions import CredenciaisInvalidas
from app.infrastructure.database.models.enums import PapelUsuario
from app.infrastructure.database.models.usuario import Usuario


class HashFake(HashDeSenha):
    """Trata o hash como 'hash:<senha>' para checagem determinística."""

    def gerar_hash(self, senha_pura: str) -> str:
        return f"hash:{senha_pura}"

    def verificar(self, senha_pura: str, hash_armazenado: str) -> bool:
        return hash_armazenado == f"hash:{senha_pura}"


class TokenFake(GeradorDeToken):
    @property
    def expira_em_segundos(self) -> int:
        return 3600

    def gerar_token_de_acesso(self, usuario_id, papel: str) -> str:
        return f"token-{usuario_id}-{papel}"

    def decodificar(self, token: str) -> DadosDoToken:
        raise NotImplementedError


class UsuarioRepoFake(UsuarioRepository):
    def __init__(self, usuarios: list[Usuario] | None = None) -> None:
        self._por_email = {u.email: u for u in (usuarios or [])}

    async def adicionar(self, usuario): ...
    async def obter_por_id(self, usuario_id): ...
    async def obter_por_email(self, email):
        return self._por_email.get(email)
    async def listar(self, usina_id, limite, deslocamento): ...
    async def atualizar(self, usuario): ...
    async def remover(self, usuario): ...


def _usuario(senha_hash: str = "hash:senhaforte123", ativo: bool = True) -> Usuario:
    return Usuario(
        id=uuid.uuid4(),
        usina_id=uuid.uuid4(),
        nome="Operador",
        email="op@usina.com",
        senha_hash=senha_hash,
        papel=PapelUsuario.OPERADOR,
        ativo=ativo,
    )


async def test_login_bem_sucedido_retorna_token():
    servico = AutenticacaoService(
        UsuarioRepoFake([_usuario()]), HashFake(), TokenFake()
    )

    resposta = await servico.autenticar("op@usina.com", "senhaforte123")

    assert resposta.access_token.startswith("token-")
    assert resposta.token_type == "bearer"
    assert resposta.expira_em_segundos == 3600


async def test_senha_incorreta_falha():
    servico = AutenticacaoService(
        UsuarioRepoFake([_usuario()]), HashFake(), TokenFake()
    )

    with pytest.raises(CredenciaisInvalidas):
        await servico.autenticar("op@usina.com", "senhaerrada")


async def test_email_inexistente_falha():
    servico = AutenticacaoService(UsuarioRepoFake([]), HashFake(), TokenFake())

    with pytest.raises(CredenciaisInvalidas):
        await servico.autenticar("naoexiste@usina.com", "qualquer")


async def test_usuario_inativo_nao_autentica():
    servico = AutenticacaoService(
        UsuarioRepoFake([_usuario(ativo=False)]), HashFake(), TokenFake()
    )

    with pytest.raises(CredenciaisInvalidas):
        await servico.autenticar("op@usina.com", "senhaforte123")
