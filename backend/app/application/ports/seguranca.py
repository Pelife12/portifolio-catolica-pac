"""Contratos de segurança usados pelos casos de uso.

Os serviços de aplicação dependem destas abstrações, nunca das implementações
concretas (bcrypt, PyJWT). Isso mantém a lógica testável com dublês e permite
trocar a biblioteca de hash ou de token sem tocar nas regras.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


class HashDeSenha(ABC):
    @abstractmethod
    def gerar_hash(self, senha_pura: str) -> str:
        """Deriva o hash a ser persistido a partir da senha em texto puro."""

    @abstractmethod
    def verificar(self, senha_pura: str, hash_armazenado: str) -> bool:
        """Confere se a senha informada corresponde ao hash armazenado."""


@dataclass(frozen=True)
class DadosDoToken:
    """Informações extraídas de um token válido."""

    usuario_id: UUID
    papel: str


class GeradorDeToken(ABC):
    @property
    @abstractmethod
    def expira_em_segundos(self) -> int:
        """Validade do token de acesso emitido, em segundos."""

    @abstractmethod
    def gerar_token_de_acesso(self, usuario_id: UUID, papel: str) -> str:
        """Emite um token de acesso assinado para o usuário."""

    @abstractmethod
    def decodificar(self, token: str) -> DadosDoToken:
        """Valida a assinatura/expiração e devolve os dados do token.

        Lança CredenciaisInvalidas/NaoAutenticado quando o token é inválido.
        """
