"""DTOs da entidade Usuário.

A senha entra apenas no DTO de criação/atualização (texto puro, sob HTTPS) e
nunca sai em nenhuma resposta — o hash não é exposto pela API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.infrastructure.database.models.enums import PapelUsuario


class UsuarioCriar(BaseModel):
    usina_id: UUID
    nome: str = Field(min_length=1, max_length=150)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    papel: PapelUsuario = PapelUsuario.OPERADOR


class UsuarioAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    senha: str | None = Field(default=None, min_length=8, max_length=128)
    papel: PapelUsuario | None = None
    ativo: bool | None = None


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usina_id: UUID
    nome: str
    email: EmailStr
    papel: PapelUsuario
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
