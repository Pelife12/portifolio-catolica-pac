"""DTOs da entidade Alerta."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.infrastructure.database.models.enums import (
    SeveridadeAlerta,
    StatusAlerta,
    TipoAlerta,
)


class AlertaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    leira_id: UUID
    afericao_id: UUID | None
    tipo: TipoAlerta
    severidade: SeveridadeAlerta
    status: StatusAlerta
    mensagem: str
    detectado_em: datetime
    reconhecido_por_id: UUID | None
    reconhecido_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime
