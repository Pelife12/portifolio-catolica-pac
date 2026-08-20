"""Schemas de entrada/saída do endpoint de health-check."""

from pydantic import BaseModel, Field


class SaudeResponse(BaseModel):
    status: str = Field(description="'operacional' quando todas as dependências respondem.")
    api: str
    banco_de_dados: str
    versao: str
    ambiente: str
