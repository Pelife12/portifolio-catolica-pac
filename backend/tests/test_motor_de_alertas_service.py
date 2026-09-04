"""Testes do MotorDeAlertasService: geração e deduplicação de alertas."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.application.ports.repositorios import (
    AfericaoRepository,
    AlertaRepository,
    LeiraRepository,
)
from app.application.services.motor_de_alertas_service import (
    MotorDeAlertasService,
    parametros_do_motor,
)
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.enums import StatusAlerta, TipoAlerta

AGORA = datetime.now(UTC)
PARAMS = parametros_do_motor(55.0, 72, 10.0)


class LeiraRepoFake(LeiraRepository):
    def __init__(self, data_montagem: datetime) -> None:
        self._leira = SimpleNamespace(id=uuid.uuid4(), data_montagem=data_montagem)

    async def adicionar(self, leira): ...
    async def obter_por_id(self, leira_id):
        return self._leira
    async def obter_por_codigo(self, usina_id, codigo): ...
    async def listar(self, usina_id, limite, deslocamento): ...
    async def atualizar(self, leira): ...
    async def remover(self, leira): ...

    @property
    def id(self):
        return self._leira.id


class AfericaoRepoFake(AfericaoRepository):
    def __init__(self, leituras: list[SimpleNamespace]) -> None:
        self._leituras = leituras

    async def adicionar(self, afericao): ...
    async def obter_por_id(self, afericao_id): ...
    async def obter_por_id_cliente(self, id_cliente): ...
    async def listar(self, leira_id, limite, deslocamento):
        return self._leituras


class AlertaRepoMemoria(AlertaRepository):
    def __init__(self) -> None:
        self.itens: list[Alerta] = []

    async def adicionar(self, alerta: Alerta) -> Alerta:
        alerta.id = uuid.uuid4()
        alerta.criado_em = AGORA
        alerta.atualizado_em = AGORA
        self.itens.append(alerta)
        return alerta

    async def obter_por_id(self, alerta_id):
        return next((a for a in self.itens if a.id == alerta_id), None)

    async def atualizar(self, alerta):
        return alerta

    async def listar(self, leira_id, status, limite, deslocamento):
        return self.itens

    async def existe_para(self, leira_id, tipo, afericao_id):
        return any(
            a.leira_id == leira_id
            and a.tipo == tipo
            and a.afericao_id == afericao_id
            for a in self.itens
        )


def _afericao(registrado_em: datetime, temperatura: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        registrado_em=registrado_em,
        temperatura_celsius=Decimal(temperatura),
    )


def _servico(leira_repo, afericao_repo, alerta_repo) -> MotorDeAlertasService:
    return MotorDeAlertasService(leira_repo, afericao_repo, alerta_repo, PARAMS)


async def test_gera_alerta_de_falta_de_termofilia_e_nao_duplica():
    montagem = AGORA - timedelta(hours=100)  # prazo de 72h já vencido
    leira_repo = LeiraRepoFake(montagem)
    afericao_repo = AfericaoRepoFake(
        [_afericao(montagem + timedelta(hours=12), "40")]  # nunca chegou a 55
    )
    alerta_repo = AlertaRepoMemoria()
    servico = _servico(leira_repo, afericao_repo, alerta_repo)

    criados = await servico.avaliar_leira(leira_repo.id)
    assert len(criados) == 1
    assert criados[0].tipo is TipoAlerta.NAO_ATINGIU_TERMOFILICA
    assert criados[0].status is StatusAlerta.ABERTO

    # Segunda avaliação não deve duplicar o mesmo alerta.
    criados_de_novo = await servico.avaliar_leira(leira_repo.id)
    assert criados_de_novo == []
    assert len(alerta_repo.itens) == 1


async def test_gera_alerta_de_queda_brusca_vinculado_a_afericao():
    montagem = AGORA - timedelta(hours=40)
    quente = _afericao(montagem + timedelta(hours=24), "65")
    fria = _afericao(montagem + timedelta(hours=30), "50")  # queda de 15 °C
    leira_repo = LeiraRepoFake(montagem)
    alerta_repo = AlertaRepoMemoria()
    servico = _servico(leira_repo, AfericaoRepoFake([quente, fria]), alerta_repo)

    criados = await servico.avaliar_leira(leira_repo.id)

    quedas = [a for a in criados if a.tipo is TipoAlerta.QUEDA_BRUSCA_TEMPERATURA]
    assert len(quedas) == 1
    assert quedas[0].afericao_id == fria.id
