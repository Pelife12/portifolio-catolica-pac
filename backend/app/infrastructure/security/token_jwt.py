"""Implementação de GeradorDeToken usando JWT (PyJWT)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.application.ports.seguranca import DadosDoToken, GeradorDeToken
from app.domain.exceptions import NaoAutenticado


class GeradorDeTokenJWT(GeradorDeToken):
    def __init__(self, segredo: str, algoritmo: str, expira_minutos: int) -> None:
        self._segredo = segredo
        self._algoritmo = algoritmo
        self._expira_minutos = expira_minutos

    @property
    def expira_em_segundos(self) -> int:
        return self._expira_minutos * 60

    def gerar_token_de_acesso(self, usuario_id: UUID, papel: str) -> str:
        agora = datetime.now(UTC)
        payload = {
            "sub": str(usuario_id),
            "papel": papel,
            "iat": agora,
            "exp": agora + timedelta(minutes=self._expira_minutos),
        }
        return jwt.encode(payload, self._segredo, algorithm=self._algoritmo)

    def decodificar(self, token: str) -> DadosDoToken:
        try:
            payload = jwt.decode(token, self._segredo, algorithms=[self._algoritmo])
        except jwt.ExpiredSignatureError as exc:
            raise NaoAutenticado("Token expirado.") from exc
        except jwt.InvalidTokenError as exc:
            raise NaoAutenticado("Token inválido.") from exc

        sub = payload.get("sub")
        papel = payload.get("papel")
        if sub is None or papel is None:
            raise NaoAutenticado("Token sem os dados necessários.")

        try:
            usuario_id = UUID(sub)
        except (ValueError, TypeError) as exc:
            raise NaoAutenticado("Identificador de usuário inválido no token.") from exc

        return DadosDoToken(usuario_id=usuario_id, papel=papel)
