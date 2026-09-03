"""Repositório da composição da leira (leira_residuos) sobre SQLAlchemy."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import LeiraResiduoRepository
from app.infrastructure.database.models.leira_residuo import LeiraResiduo


class LeiraResiduoRepositorySQLAlchemy(LeiraResiduoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def listar_por_leira(self, leira_id: UUID) -> list[LeiraResiduo]:
        resultado = await self._session.execute(
            select(LeiraResiduo).where(LeiraResiduo.leira_id == leira_id)
        )
        return list(resultado.scalars().all())

    async def substituir_composicao(
        self, leira_id: UUID, componentes: list[tuple[UUID, Decimal]]
    ) -> list[LeiraResiduo]:
        # Troca atômica: remove a composição atual e insere a nova. A operação
        # inteira roda na mesma transação da requisição (commit no fim).
        await self._session.execute(
            delete(LeiraResiduo).where(LeiraResiduo.leira_id == leira_id)
        )
        novos = [
            LeiraResiduo(leira_id=leira_id, residuo_id=residuo_id, massa_kg=massa)
            for residuo_id, massa in componentes
        ]
        self._session.add_all(novos)
        await self._session.flush()
        return novos
