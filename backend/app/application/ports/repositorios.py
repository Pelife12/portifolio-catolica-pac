"""Portas de persistência (repository pattern).

Cada serviço de aplicação depende destas interfaces; as implementações
concretas em SQLAlchemy vivem na camada de infraestrutura. Os métodos operam
sobre os modelos do banco, que aqui exercem o papel de entidades persistentes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from decimal import Decimal

from app.infrastructure.database.models.afericao import Afericao
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.enums import StatusAlerta, TipoAlerta
from app.infrastructure.database.models.leira import Leira
from app.infrastructure.database.models.leira_residuo import LeiraResiduo
from app.infrastructure.database.models.residuo import Residuo
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


class AfericaoRepository(ABC):
    @abstractmethod
    async def adicionar(self, afericao: Afericao) -> Afericao: ...

    @abstractmethod
    async def obter_por_id(self, afericao_id: UUID) -> Afericao | None: ...

    @abstractmethod
    async def obter_por_id_cliente(self, id_cliente: UUID) -> Afericao | None: ...

    @abstractmethod
    async def listar(
        self, leira_id: UUID | None, limite: int, deslocamento: int
    ) -> list[Afericao]: ...


class AlertaRepository(ABC):
    @abstractmethod
    async def adicionar(self, alerta: Alerta) -> Alerta: ...

    @abstractmethod
    async def obter_por_id(self, alerta_id: UUID) -> Alerta | None: ...

    @abstractmethod
    async def atualizar(self, alerta: Alerta) -> Alerta: ...

    @abstractmethod
    async def listar(
        self,
        leira_id: UUID | None,
        status: StatusAlerta | None,
        limite: int,
        deslocamento: int,
    ) -> list[Alerta]: ...

    @abstractmethod
    async def existe_para(
        self, leira_id: UUID, tipo: TipoAlerta, afericao_id: UUID | None
    ) -> bool:
        """Indica se já há um alerta do mesmo tipo/aferição (evita duplicação)."""


class ResiduoRepository(ABC):
    @abstractmethod
    async def adicionar(self, residuo: Residuo) -> Residuo: ...

    @abstractmethod
    async def obter_por_id(self, residuo_id: UUID) -> Residuo | None: ...

    @abstractmethod
    async def obter_por_ids(self, ids: list[UUID]) -> list[Residuo]: ...

    @abstractmethod
    async def obter_por_nome(self, nome: str) -> Residuo | None: ...

    @abstractmethod
    async def listar(self, limite: int, deslocamento: int) -> list[Residuo]: ...


class LeiraResiduoRepository(ABC):
    @abstractmethod
    async def listar_por_leira(self, leira_id: UUID) -> list[LeiraResiduo]: ...

    @abstractmethod
    async def substituir_composicao(
        self, leira_id: UUID, componentes: list[tuple[UUID, Decimal]]
    ) -> list[LeiraResiduo]:
        """Substitui toda a composição da leira pela lista (residuo_id, massa_kg)."""


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
