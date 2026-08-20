"""Repositório de Usina sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import UsinaRepository
from app.infrastructure.database.models.usina import Usina


class UsinaRepositorySQLAlchemy(UsinaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, usina: Usina) -> Usina:
        self._session.add(usina)
        await self._session.flush()
        return usina

    async def obter_por_id(self, usina_id: UUID) -> Usina | None:
        return await self._session.get(Usina, usina_id)

    async def listar(self, limite: int, deslocamento: int) -> list[Usina]:
        resultado = await self._session.execute(
            select(Usina).order_by(Usina.nome).limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())

    async def atualizar(self, usina: Usina) -> Usina:
        await self._session.flush()
        return usina

    async def remover(self, usina: Usina) -> None:
        await self._session.delete(usina)
        await self._session.flush()
