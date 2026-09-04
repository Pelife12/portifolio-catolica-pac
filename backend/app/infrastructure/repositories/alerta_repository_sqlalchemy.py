"""Repositório de Alerta sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import AlertaRepository
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.enums import StatusAlerta, TipoAlerta


class AlertaRepositorySQLAlchemy(AlertaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, alerta: Alerta) -> Alerta:
        self._session.add(alerta)
        await self._session.flush()
        return alerta

    async def obter_por_id(self, alerta_id: UUID) -> Alerta | None:
        return await self._session.get(Alerta, alerta_id)

    async def atualizar(self, alerta: Alerta) -> Alerta:
        await self._session.flush()
        return alerta

    async def listar(
        self,
        leira_id: UUID | None,
        status: StatusAlerta | None,
        limite: int,
        deslocamento: int,
    ) -> list[Alerta]:
        consulta = select(Alerta).order_by(Alerta.detectado_em.desc())
        if leira_id is not None:
            consulta = consulta.where(Alerta.leira_id == leira_id)
        if status is not None:
            consulta = consulta.where(Alerta.status == status)
        resultado = await self._session.execute(
            consulta.limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())

    async def existe_para(
        self, leira_id: UUID, tipo: TipoAlerta, afericao_id: UUID | None
    ) -> bool:
        consulta = (
            select(func.count())
            .select_from(Alerta)
            .where(Alerta.leira_id == leira_id, Alerta.tipo == tipo)
        )
        # afericao_id nulo (ex.: alerta de fase termofílica) é comparado com IS NULL.
        if afericao_id is None:
            consulta = consulta.where(Alerta.afericao_id.is_(None))
        else:
            consulta = consulta.where(Alerta.afericao_id == afericao_id)

        resultado = await self._session.execute(consulta)
        return (resultado.scalar_one() or 0) > 0
