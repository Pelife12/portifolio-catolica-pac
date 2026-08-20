"""Fixtures compartilhadas dos testes."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_verificador_de_saude
from app.domain.repositories.verificador_de_saude import VerificadorDeSaudeDoBanco
from app.main import criar_app


class VerificadorDeSaudeFake(VerificadorDeSaudeDoBanco):
    """Dublê de teste: dispensa um PostgreSQL real para testar a camada de API."""

    def __init__(self, disponivel: bool = True) -> None:
        self.disponivel = disponivel

    async def esta_disponivel(self) -> bool:
        return self.disponivel


@pytest.fixture
def app():
    return criar_app()


@pytest.fixture
def verificador_fake() -> VerificadorDeSaudeFake:
    return VerificadorDeSaudeFake()


@pytest.fixture
async def client(app, verificador_fake) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_verificador_de_saude] = lambda: verificador_fake
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
