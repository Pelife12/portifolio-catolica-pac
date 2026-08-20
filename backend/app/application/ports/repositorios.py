"""Portas de persistência (repository pattern).

Cada serviço de aplicação depende destas interfaces; as implementações
concretas em SQLAlchemy vivem na camada de infraestrutura. Os métodos operam
sobre os modelos do banco, que aqui exercem o papel de entidades persistentes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.infrastructure.database.models.leira import Leira
from app.infrastructure.database.models.usina import Usina
from app.infrastructure.database.models.usuario import Usuario


class UsinaRepository(ABC):
    @abstractmethod
    async def adicionar(self, usina: Usina) -> Usina: ...

    @abstractmethod
    async def obter_por_id(self, usina_id: UUID) -> Usina | None: ...

    @abstractmethod
    async def listar(self, limite: int, deslocamento: int) -> list[Usina]: ...

    @abstractmethod
    async def atualizar(self, usina: Usina) -> Usina: ...

    @abstractmethod
    async def remover(self, usina: Usina) -> None: ...


class UsuarioRepository(ABC):
    @abstractmethod
    async def adicionar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    async def obter_por_id(self, usuario_id: UUID) -> Usuario | None: ...

    @abstractmethod
    async def obter_por_email(self, email: str) -> Usuario | None: ...

    @abstractmethod
    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Usuario]: ...

    @abstractmethod
    async def atualizar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    async def remover(self, usuario: Usuario) -> None: ...


class LeiraRepository(ABC):
    @abstractmethod
    async def adicionar(self, leira: Leira) -> Leira: ...

    @abstractmethod
    async def obter_por_id(self, leira_id: UUID) -> Leira | None: ...

    @abstractmethod
    async def obter_por_codigo(self, usina_id: UUID, codigo: str) -> Leira | None: ...

    @abstractmethod
    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Leira]: ...

    @abstractmethod
    async def atualizar(self, leira: Leira) -> Leira: ...

    @abstractmethod
    async def remover(self, leira: Leira) -> None: ...
