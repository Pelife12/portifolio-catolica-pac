"""Casos de uso de Resíduo (base de conhecimento do traço)."""

from uuid import UUID

from app.application.dto.residuo import ResiduoCriar, ResiduoResponse
from app.application.ports.repositorios import ResiduoRepository
from app.domain.exceptions import EntidadeDuplicada, RecursoNaoEncontrado
from app.infrastructure.database.models.residuo import Residuo


class ResiduoService:
    def __init__(self, residuo_repo: ResiduoRepository) -> None:
        self._repo = residuo_repo

    async def criar(self, dados: ResiduoCriar) -> ResiduoResponse:
        if await self._repo.obter_por_nome(dados.nome) is not None:
            raise EntidadeDuplicada("Já existe um resíduo com esse nome.")
        residuo = Residuo(
            nome=dados.nome,
            categoria=dados.categoria,
            percentual_carbono=dados.percentual_carbono,
            percentual_nitrogenio=dados.percentual_nitrogenio,
            teor_umidade_percentual=dados.teor_umidade_percentual,
        )
        residuo = await self._repo.adicionar(residuo)
        return ResiduoResponse.model_validate(residuo)

    async def listar(self, limite: int, deslocamento: int) -> list[ResiduoResponse]:
        residuos = await self._repo.listar(limite, deslocamento)
        return [ResiduoResponse.model_validate(r) for r in residuos]

    async def obter(self, residuo_id: UUID) -> ResiduoResponse:
        residuo = await self._repo.obter_por_id(residuo_id)
        if residuo is None:
            raise RecursoNaoEncontrado("Resíduo não encontrado.")
        return ResiduoResponse.model_validate(residuo)
