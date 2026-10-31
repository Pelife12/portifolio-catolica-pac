"""Repositório de Aferição sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import AfericaoRepository
from app.domain.exceptions import EntidadeDuplicada
from app.infrastructure.database.models.afericao import Afericao


class AfericaoRepositorySQLAlchemy(AfericaoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, afericao: Afericao) -> Afericao:
        # Savepoint: se o id_cliente colidir (reenvio simultâneo da página e do
        # Service Worker), só a inserção é desfeita e a transação da requisição
        # continua utilizável para buscar o registro que venceu a corrida.
        try:
            async with self._session.begin_nested():
                self._session.add(afericao)
                await self._session.flush()
        except IntegrityError as erro:
            if "id_cliente" in str(erro.orig):
                raise EntidadeDuplicada("Aferição já sincronizada (id_cliente repetido).") from erro
            raise
        return afericao

    async def obter_por_id(self, afericao_id: UUID) -> Afericao | None:
        return await self._session.get(Afericao, afericao_id)

    async def obter_por_id_cliente(self, id_cliente: UUID) -> Afericao | None:
        resultado = await self._session.execute(
            select(Afericao).where(Afericao.id_cliente == id_cliente)
        )
        return resultado.scalar_one_or_none()

    async def listar(
        self, leira_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Afericao]:
        consulta = select(Afericao).order_by(Afericao.registrado_em.desc())
        if leira_id is not None:
            consulta = consulta.where(Afericao.leira_id == leira_id)
        resultado = await self._session.execute(
            consulta.limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())
