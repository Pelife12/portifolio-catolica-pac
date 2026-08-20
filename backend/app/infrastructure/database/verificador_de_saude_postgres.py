"""Implementação PostgreSQL da porta de verificação de saúde."""

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.verificador_de_saude import VerificadorDeSaudeDoBanco

logger = logging.getLogger(__name__)


class VerificadorDeSaudePostgres(VerificadorDeSaudeDoBanco):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def esta_disponivel(self) -> bool:
        try:
            await self._session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            logger.exception("Falha ao consultar o banco de dados no health-check")
            return False
        return True
