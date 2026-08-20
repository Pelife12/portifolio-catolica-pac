"""Entidade que representa o estado de saúde da aplicação."""

from dataclasses import dataclass
from enum import Enum


class EstadoDependencia(str, Enum):
    OPERACIONAL = "operacional"
    INDISPONIVEL = "indisponivel"


@dataclass(frozen=True)
class StatusSaude:
    """Resultado da verificação de saúde da API e de suas dependências."""

    api: EstadoDependencia
    banco_de_dados: EstadoDependencia

    @property
    def operacional(self) -> bool:
        """A aplicação só é considerada saudável se todas as dependências estiverem de pé."""
        return (
            self.api is EstadoDependencia.OPERACIONAL
            and self.banco_de_dados is EstadoDependencia.OPERACIONAL
        )
