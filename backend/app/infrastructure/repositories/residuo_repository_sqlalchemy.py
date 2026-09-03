"""Repositório de Resíduo sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import ResiduoRepository
from app.infrastructure.database.models.residuo import Residuo


class ResiduoRepositorySQLAlchemy(ResiduoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, residuo: Residuo) -> Residuo:
        self._session.add(residuo)
        await self._session.flush()
        return residuo

    async def obter_por_id(self, residuo_id: UUID) -> Residuo | None:
        return await self._session.get(Residuo, residuo_id)

    async def obter_por_ids(self, ids: list[UUID]) -> list[Residuo]:
        if not ids:
            return []
        resultado = await self._session.execute(
            select(Residuo).where(Residuo.id.in_(ids))
        )
        return list(resultado.scalars().all())

    async def obter_por_nome(self, nome: str) -> Residuo | None:
        resultado = await self._session.execute(
            select(Residuo).where(Residuo.nome == nome)
        )
        return resultado.scalar_one_or_none()

    async def listar(self, limite: int, deslocamento: int) -> list[Residuo]:
        resultado = await self._session.execute(
            select(Residuo).order_by(Residuo.nome).limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())
