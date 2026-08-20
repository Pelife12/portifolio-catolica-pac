"""Repositório de Usuário sobre SQLAlchemy assíncrono."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import UsuarioRepository
from app.infrastructure.database.models.usuario import Usuario


class UsuarioRepositorySQLAlchemy(UsuarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def adicionar(self, usuario: Usuario) -> Usuario:
        self._session.add(usuario)
        await self._session.flush()
        return usuario

    async def obter_por_id(self, usuario_id: UUID) -> Usuario | None:
        return await self._session.get(Usuario, usuario_id)

    async def obter_por_email(self, email: str) -> Usuario | None:
        resultado = await self._session.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return resultado.scalar_one_or_none()

    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Usuario]:
        consulta = select(Usuario).order_by(Usuario.nome)
        if usina_id is not None:
            consulta = consulta.where(Usuario.usina_id == usina_id)
        resultado = await self._session.execute(
            consulta.limit(limite).offset(deslocamento)
        )
        return list(resultado.scalars().all())

    async def atualizar(self, usuario: Usuario) -> Usuario:
        await self._session.flush()
        return usuario

    async def remover(self, usuario: Usuario) -> None:
        await self._session.delete(usuario)
        await self._session.flush()
