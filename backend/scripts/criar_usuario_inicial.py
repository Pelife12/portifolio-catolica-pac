"""Cria a usina e o usuário administrador iniciais (bootstrap).

Resolve o problema do "ovo e a galinha": os endpoints de cadastro exigem
autenticação, mas sem nenhum usuário não há como fazer login. Este script cria
o primeiro administrador diretamente no banco.

Uso (dentro do container):
    docker compose exec api python -m scripts.criar_usuario_inicial \
        --nome "Admin" --email admin@usina.com --senha "senhaforte123"

Se a usina ou o e-mail já existirem, o script não duplica.
"""

import argparse
import asyncio

from sqlalchemy import select

from app.infrastructure.database.models.enums import PapelUsuario
from app.infrastructure.database.models.usina import Usina
from app.infrastructure.database.models.usuario import Usuario
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.security.hash_bcrypt import HashDeSenhaBcrypt


async def criar(nome: str, email: str, senha: str, nome_usina: str) -> None:
    hash_de_senha = HashDeSenhaBcrypt()

    async with SessionLocal() as session:
        usina = (
            await session.execute(select(Usina).where(Usina.nome == nome_usina))
        ).scalar_one_or_none()
        if usina is None:
            usina = Usina(nome=nome_usina)
            session.add(usina)
            await session.flush()
            print(f"Usina criada: {usina.nome} ({usina.id})")
        else:
            print(f"Usina já existia: {usina.nome} ({usina.id})")

        existente = (
            await session.execute(select(Usuario).where(Usuario.email == email))
        ).scalar_one_or_none()
        if existente is not None:
            print(f"Usuário com e-mail {email} já existe. Nada a fazer.")
            return

        usuario = Usuario(
            usina_id=usina.id,
            nome=nome,
            email=email,
            senha_hash=hash_de_senha.gerar_hash(senha),
            papel=PapelUsuario.ADMINISTRADOR,
        )
        session.add(usuario)
        await session.commit()
        print(f"Administrador criado: {usuario.email} ({usuario.id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria o administrador inicial.")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--senha", required=True)
    parser.add_argument("--usina", default="Usina Matriz")
    args = parser.parse_args()

    asyncio.run(criar(args.nome, args.email, args.senha, args.usina))


if __name__ == "__main__":
    main()
