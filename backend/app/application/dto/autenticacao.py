"""DTOs de autenticação."""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expira_em_segundos: int = Field(description="Validade do token, em segundos.")
