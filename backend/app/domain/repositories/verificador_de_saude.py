"""Porta (interface) para verificação de disponibilidade do banco de dados.

O domínio declara o contrato; a implementação concreta vive na camada de
infraestrutura. Isso mantém a inversão de dependência (D do SOLID).
"""

from abc import ABC, abstractmethod


class VerificadorDeSaudeDoBanco(ABC):
    @abstractmethod
    async def esta_disponivel(self) -> bool:
        """Retorna True se o banco de dados responder a uma consulta trivial."""
        raise NotImplementedError
