"""Repositório de Leira sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import LeiraRepository
from app.infrastructure.database.models.leira import Leira


class LeiraRepositorySQLAlchemy(LeiraRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, leira: Leira) -> Leira:
        self._session.add(leira)
        await self._session.flush()
        return leira

    async def obter_por_id(self, leira_id: UUID) -> Leira | None:
        return await self._session.get(Leira, leira_id)

    async def obter_por_codigo(self, usina_id: UUID, codigo: str) -> Leira | None:
        resultado = await self._session.execute(
            select(Leira).where(Leira.usina_id == usina_id, Leira.codigo == codigo)
        )
        return resultado.scalar_one_or_none()

    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Leira]:
        consulta = select(Leira).order_by(Leira.data_montagem.desc())
        if usina_id is not None:
            consulta = consulta.where(Leira.usina_id == usina_id)
        resultado = await self._session.execute(
            consulta.limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())

    async def atualizar(self, leira: Leira) -> Leira:
        await self._session.flush()
        return leira

    async def remover(self, leira: Leira) -> None:
        await self._session.delete(leira)
        await self._session.flush()
