"""Casos de uso de Usina (CRUD)."""

from uuid import UUID

from app.application.dto.usina import UsinaAtualizar, UsinaCriar, UsinaResponse
from app.application.ports.repositorios import UsinaRepository
from app.domain.exceptions import RecursoNaoEncontrado
from app.infrastructure.database.models.usina import Usina


class UsinaService:
    def __init__(self, usina_repo: UsinaRepository) -> None:
        self._repo = usina_repo

    async def criar(self, dados: UsinaCriar) -> UsinaResponse:
        usina = Usina(
            nome=dados.nome,
            cnpj=dados.cnpj,
            endereco=dados.endereco,
            latitude=dados.latitude,
            longitude=dados.longitude,
        )
        usina = await self._repo.adicionar(usina)
        return UsinaResponse.model_validate(usina)

    async def listar(self, limite: int, deslocamento: int) -> list[UsinaResponse]:
        usinas = await self._repo.listar(limite, deslocamento)
        return [UsinaResponse.model_validate(u) for u in usinas]

    async def obter(self, usina_id: UUID) -> UsinaResponse:
        return UsinaResponse.model_validate(await self._obter_ou_falhar(usina_id))

    async def atualizar(self, usina_id: UUID, dados: UsinaAtualizar) -> UsinaResponse:
        usina = await self._obter_ou_falhar(usina_id)
        # exclude_unset: aplica só os campos enviados (PATCH parcial).
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(usina, campo, valor)
        usina = await self._repo.atualizar(usina)
        return UsinaResponse.model_validate(usina)

    async def remover(self, usina_id: UUID) -> None:
        usina = await self._obter_ou_falhar(usina_id)
        await self._repo.remover(usina)

    async def _obter_ou_falhar(self, usina_id: UUID) -> Usina:
        usina = await self._repo.obter_por_id(usina_id)
        if usina is None:
            raise RecursoNaoEncontrado("Usina não encontrada.")
        return usina
