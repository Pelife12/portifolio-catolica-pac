"""Testes do TracoService: orquestração entre resíduos e o cálculo do domínio."""

import uuid
from decimal import Decimal

import pytest

from app.application.dto.traco import ItemComposicao
from app.application.ports.repositorios import ResiduoRepository
from app.application.services.traco_service import TracoService
from app.domain.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from app.infrastructure.database.models.enums import CategoriaResiduo
from app.infrastructure.database.models.residuo import Residuo


class ResiduoRepoFake(ResiduoRepository):
    def __init__(self, residuos: list[Residuo]) -> None:
        self._por_id = {r.id: r for r in residuos}

    async def adicionar(self, residuo): ...
    async def obter_por_id(self, residuo_id):
        return self._por_id.get(residuo_id)
    async def obter_por_ids(self, ids):
        return [self._por_id[i] for i in ids if i in self._por_id]
    async def obter_por_nome(self, nome): ...
    async def listar(self, limite, deslocamento): ...


def _residuo(carbono, nitrogenio, umidade, ativo=True) -> Residuo:
    return Residuo(
        id=uuid.uuid4(),
        nome=f"R-{uuid.uuid4().hex[:6]}",
        categoria=CategoriaResiduo.RICO_EM_CARBONO,
        percentual_carbono=Decimal(str(carbono)),
        percentual_nitrogenio=Decimal(str(nitrogenio)),
        teor_umidade_percentual=Decimal(str(umidade)),
        ativo=ativo,
    )


def _servico(residuos: list[Residuo]) -> TracoService:
    # leira_repo e leira_residuo_repo não são usados no cálculo avulso.
    return TracoService(ResiduoRepoFake(residuos), leira_repo=None, leira_residuo_repo=None)


async def test_calcular_resolve_residuos_e_retorna_traco():
    r1 = _residuo(carbono=40, nitrogenio=1, umidade=0)
    r2 = _residuo(carbono=20, nitrogenio=4, umidade=0)
    servico = _servico([r1, r2])

    itens = [
        ItemComposicao(residuo_id=r1.id, massa_kg=Decimal("100")),
        ItemComposicao(residuo_id=r2.id, massa_kg=Decimal("100")),
    ]
    resultado = await servico.calcular(itens)

    assert resultado.relacao_cn == Decimal("12.00")


async def test_residuo_repetido_e_rejeitado():
    r1 = _residuo(carbono=40, nitrogenio=1, umidade=0)
    servico = _servico([r1])

    itens = [
        ItemComposicao(residuo_id=r1.id, massa_kg=Decimal("50")),
        ItemComposicao(residuo_id=r1.id, massa_kg=Decimal("50")),
    ]
    with pytest.raises(RegraDeNegocioViolada, match="repetido"):
        await servico.calcular(itens)


async def test_residuo_inexistente_falha():
    servico = _servico([])

    itens = [ItemComposicao(residuo_id=uuid.uuid4(), massa_kg=Decimal("10"))]
    with pytest.raises(RecursoNaoEncontrado):
        await servico.calcular(itens)


async def test_residuo_inativo_e_rejeitado():
    r1 = _residuo(carbono=40, nitrogenio=1, umidade=0, ativo=False)
    servico = _servico([r1])

    itens = [ItemComposicao(residuo_id=r1.id, massa_kg=Decimal("100"))]
    with pytest.raises(RegraDeNegocioViolada, match="inativo"):
        await servico.calcular(itens)
