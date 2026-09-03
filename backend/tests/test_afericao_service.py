"""Testes do AfericaoService: trava temporal, idempotência e dados de auditoria."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.application.dto.afericao import AfericaoCriar
from app.application.ports.repositorios import AfericaoRepository, LeiraRepository
from app.application.services.afericao_service import AfericaoService
from app.domain.exceptions import AfericaoForaDaJanela, RecursoNaoEncontrado
from app.infrastructure.database.models.afericao import Afericao


class AfericaoRepoFake(AfericaoRepository):
    def __init__(self) -> None:
        self.itens: list[Afericao] = []

    async def adicionar(self, afericao: Afericao) -> Afericao:
        afericao.id = uuid.uuid4()
        afericao.sincronizado_em = datetime.now(UTC)
        self.itens.append(afericao)
        return afericao

    async def obter_por_id(self, afericao_id):
        return next((a for a in self.itens if a.id == afericao_id), None)

    async def obter_por_id_cliente(self, id_cliente):
        return next((a for a in self.itens if a.id_cliente == id_cliente), None)

    async def listar(self, leira_id, limite, deslocamento):
        return self.itens


class LeiraRepoFake(LeiraRepository):
    def __init__(self, leira_existe: bool = True) -> None:
        self._existe = leira_existe

    async def adicionar(self, leira): ...
    async def obter_por_id(self, leira_id):
        return object() if self._existe else None
    async def obter_por_codigo(self, usina_id, codigo): ...
    async def listar(self, usina_id, limite, deslocamento): ...
    async def atualizar(self, leira): ...
    async def remover(self, leira): ...


def _dados(registrado_em: datetime, id_cliente=None) -> AfericaoCriar:
    return AfericaoCriar(
        leira_id=uuid.uuid4(),
        temperatura_celsius=Decimal("58.5"),
        umidade_percentual=Decimal("55"),
        registrado_em=registrado_em,
        latitude=Decimal("-26.9"),
        longitude=Decimal("-49.07"),
        id_cliente=id_cliente,
    )


def _servico(afericao_repo=None, leira_existe=True) -> AfericaoService:
    return AfericaoService(
        afericao_repo or AfericaoRepoFake(),
        LeiraRepoFake(leira_existe),
        janela_retroativa_horas=24,
    )


async def test_registra_afericao_valida_com_usuario_do_token():
    servico = _servico()
    usuario_id = uuid.uuid4()

    afericao, criada = await servico.registrar(
        _dados(datetime.now(UTC)), usuario_id=usuario_id
    )

    assert criada is True
    assert afericao.usuario_id == usuario_id  # RNF01: usuário autenticado


async def test_coleta_retroativa_alem_de_24h_e_rejeitada():
    servico = _servico()

    with pytest.raises(AfericaoForaDaJanela):
        await servico.registrar(
            _dados(datetime.now(UTC) - timedelta(hours=25)), usuario_id=uuid.uuid4()
        )


async def test_leira_inexistente_falha():
    servico = _servico(leira_existe=False)

    with pytest.raises(RecursoNaoEncontrado):
        await servico.registrar(_dados(datetime.now(UTC)), usuario_id=uuid.uuid4())


async def test_reenvio_com_mesmo_id_cliente_e_idempotente():
    repo = AfericaoRepoFake()
    servico = _servico(afericao_repo=repo)
    id_cliente = uuid.uuid4()

    _, criada1 = await servico.registrar(
        _dados(datetime.now(UTC), id_cliente=id_cliente), usuario_id=uuid.uuid4()
    )
    _, criada2 = await servico.registrar(
        _dados(datetime.now(UTC), id_cliente=id_cliente), usuario_id=uuid.uuid4()
    )

    assert criada1 is True
    assert criada2 is False  # segundo envio não cria novo registro
    assert len(repo.itens) == 1
