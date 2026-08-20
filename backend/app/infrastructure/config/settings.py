"""Configuração da aplicação, carregada de variáveis de ambiente."""

from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplicação
    nome_app: str = "API de Rastreabilidade de Compostagem"
    versao_app: str = "0.1.0"
    ambiente: str = Field(default="desenvolvimento")
    debug: bool = Field(default=False)

    # Banco de dados
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://compostagem:compostagem@localhost:5432/compostagem"
    )
    db_echo: bool = Field(default=False)
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)

    # CORS: origens liberadas para o PWA em React
    origens_permitidas: list[str] = Field(default=["http://localhost:5173"])

    # Regras de negócio parametrizáveis (usadas a partir da Sprint 2)
    janela_retroativa_horas: int = Field(default=24)
    temperatura_termofilica_minima: float = Field(default=55.0)
    prazo_fase_termofilica_horas: int = Field(default=72)


@lru_cache
def get_settings() -> Settings:
    """Cacheado para que o .env seja lido uma única vez por processo."""
    return Settings()
