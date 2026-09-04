"""Casos de uso de gestão de Alerta: consulta, reconhecimento e resolução."""

from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.alerta import AlertaResponse
from app.application.ports.repositorios import AlertaRepository
from app.domain.exceptions import RecursoNaoEncontrado
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.enums import StatusAlerta


class AlertaService:
    def __init__(self, alerta_repo: AlertaRepository) -> None:
        self._repo = alerta_repo

    async def listar(
        self,
        leira_id: UUID | None,
        status: StatusAlerta | None,
        limite: int,
        deslocamento: int,
    ) -> list[AlertaResponse]:
        alertas = await self._repo.listar(leira_id, status, limite, deslocamento)
        return [AlertaResponse.model_validate(a) for a in alertas]

    async def obter(self, alerta_id: UUID) -> AlertaResponse:
        return AlertaResponse.model_validate(await self._obter_ou_falhar(alerta_id))

    async def reconhecer(self, alerta_id: UUID, usuario_id: UUID) -> AlertaResponse:
        alerta = await self._obter_ou_falhar(alerta_id)
        alerta.status = StatusAlerta.RECONHECIDO
        alerta.reconhecido_por_id = usuario_id
        alerta.reconhecido_em = datetime.now(UTC)
        return AlertaResponse.model_validate(await self._repo.atualizar(alerta))

    async def resolver(self, alerta_id: UUID) -> AlertaResponse:
        alerta = await self._obter_ou_falhar(alerta_id)
        alerta.status = StatusAlerta.RESOLVIDO
        return AlertaResponse.model_validate(await self._repo.atualizar(alerta))

    async def _obter_ou_falhar(self, alerta_id: UUID) -> Alerta:
        alerta = await self._repo.obter_por_id(alerta_id)
        if alerta is None:
            raise RecursoNaoEncontrado("Alerta não encontrado.")
        return alerta
