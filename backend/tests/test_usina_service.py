"""Testes do CRUD de Usina no nível de serviço, com repositório em memória."""

import uuid
from datetime import UTC, datetime

import pytest

from app.application.dto.usina import UsinaAtualizar, UsinaCriar
from app.application.ports.repositorios import UsinaRepository
from app.application.services.usina_service import UsinaService
from app.domain.exceptions import RecursoNaoEncontrado
from app.infrastructure.database.models.usina import Usina


class UsinaRepoMemoria(UsinaRepository):
    """Implementação em memória do port, para testar o serviço isoladamente."""

    def __init__(self) -> None:
        self._dados: dict[uuid.UUID, Usina] = {}

    async def adicionar(self, usina: Usina) -> Usina:
        # Simula os defaults que o banco preencheria no flush (pk, ativa e carimbos).
        if usina.id is None:
            usina.id = uuid.uuid4()
        if usina.ativa is None:
            usina.ativa = True
        agora = datetime.now(UTC)
        usina.criado_em = usina.criado_em or agora
        usina.atualizado_em = agora
        self._dados[usina.id] = usina
        return usina

    async def obter_por_id(self, usina_id):
        return self._dados.get(usina_id)

    async def listar(self, limite, deslocamento):
        return list(self._dados.values())[deslocamento : deslocamento + limite]

    async def atualizar(self, usina: Usina) -> Usina:
        self._dados[usina.id] = usina
        return usina

    async def remover(self, usina: Usina) -> None:
        self._dados.pop(usina.id, None)


def _servico() -> UsinaService:
    return UsinaService(UsinaRepoMemoria())


async def test_criar_e_obter_usina():
    servico = _servico()

    criada = await servico.criar(UsinaCriar(nome="Usina Vale Verde"))
    obtida = await servico.obter(criada.id)

    assert obtida.nome == "Usina Vale Verde"
    assert obtida.ativa is True


async def test_atualizacao_parcial_altera_apenas_campos_enviados():
    servico = _servico()
    criada = await servico.criar(UsinaCriar(nome="Usina Antiga", endereco="Rua A"))

    atualizada = await servico.atualizar(criada.id, UsinaAtualizar(nome="Usina Nova"))

    assert atualizada.nome == "Usina Nova"
    assert atualizada.endereco == "Rua A"  # não foi enviado, deve permanecer


async def test_obter_inexistente_falha():
    servico = _servico()

    with pytest.raises(RecursoNaoEncontrado):
        await servico.obter(uuid.uuid4())


async def test_remover_usina():
    servico = _servico()
    criada = await servico.criar(UsinaCriar(nome="Usina Temporária"))

    await servico.remover(criada.id)

    with pytest.raises(RecursoNaoEncontrado):
        await servico.obter(criada.id)
