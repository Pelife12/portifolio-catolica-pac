"""Popula a base de conhecimento com um catálogo inicial de resíduos.

Valores agronômicos aproximados (percentual de carbono e nitrogênio em base seca
e teor de umidade típico), usados como referência para o cálculo de traço. O
operador pode ajustar/expandir o catálogo pela API depois.

Uso (dentro do container):
    docker compose exec api python -m scripts.seed_residuos

O script é idempotente: resíduos já cadastrados (pelo nome) não são duplicados.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.infrastructure.database.models.enums import CategoriaResiduo
from app.infrastructure.database.models.residuo import Residuo
from app.infrastructure.database.session import SessionLocal

# (nome, categoria, %carbono, %nitrogênio, %umidade)
CATALOGO = [
    ("Esterco bovino", CategoriaResiduo.RICO_EM_NITROGENIO, "30", "1.7", "75"),
    ("Cama de frango", CategoriaResiduo.RICO_EM_NITROGENIO, "30", "3.0", "40"),
    ("Restos de hortaliças", CategoriaResiduo.RICO_EM_NITROGENIO, "45", "2.5", "80"),
    ("Grama verde (poda)", CategoriaResiduo.RICO_EM_NITROGENIO, "40", "3.0", "80"),
    ("Borra de café", CategoriaResiduo.RICO_EM_NITROGENIO, "50", "2.0", "55"),
    ("Serragem", CategoriaResiduo.RICO_EM_CARBONO, "50", "0.1", "20"),
    ("Folhas secas", CategoriaResiduo.RICO_EM_CARBONO, "45", "0.9", "15"),
    ("Palha de arroz", CategoriaResiduo.RICO_EM_CARBONO, "45", "1.0", "12"),
    ("Maravalha de madeira", CategoriaResiduo.RICO_EM_CARBONO, "50", "0.2", "18"),
    ("Papelão picado", CategoriaResiduo.RICO_EM_CARBONO, "45", "0.2", "10"),
]


async def semear() -> None:
    inseridos = 0
    async with SessionLocal() as session:
        for nome, categoria, carbono, nitrogenio, umidade in CATALOGO:
            existe = (
                await session.execute(select(Residuo).where(Residuo.nome == nome))
            ).scalar_one_or_none()
            if existe is not None:
                continue
            session.add(
                Residuo(
                    nome=nome,
                    categoria=categoria,
                    percentual_carbono=Decimal(carbono),
                    percentual_nitrogenio=Decimal(nitrogenio),
                    teor_umidade_percentual=Decimal(umidade),
                )
            )
            inseridos += 1
        await session.commit()

    print(f"Seed concluído. Resíduos inseridos: {inseridos} (de {len(CATALOGO)}).")


if __name__ == "__main__":
    asyncio.run(semear())
