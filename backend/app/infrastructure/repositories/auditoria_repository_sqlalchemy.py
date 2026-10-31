"""Repositório da trilha de auditoria sobre SQLAlchemy assíncrono."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositorios import AuditoriaRepository
from app.infrastructure.database.models.audit_log import AuditLog


class AuditoriaRepositorySQLAlchemy(AuditoriaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def registrar(self, registro: AuditLog) -> AuditLog:
        self._session.add(registro)
        await self._session.flush()
        return registro
