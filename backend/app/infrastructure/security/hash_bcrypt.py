"""Implementação de HashDeSenha usando bcrypt (via passlib)."""

from passlib.context import CryptContext

from app.application.ports.seguranca import HashDeSenha

_contexto = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashDeSenhaBcrypt(HashDeSenha):
    def gerar_hash(self, senha_pura: str) -> str:
        return _contexto.hash(senha_pura)

    def verificar(self, senha_pura: str, hash_armazenado: str) -> bool:
        return _contexto.verify(senha_pura, hash_armazenado)
