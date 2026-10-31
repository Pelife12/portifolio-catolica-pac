"""Popula o banco com uma usina de demonstração para a apresentação de 03/12.

Cria uma usina, um gestor, um operador e três leiras que cobrem os três
desfechos do ciclo, para o fluxo ponta a ponta poder ser mostrado sem esperar
dias de compostagem real:

* LR-101 — montada há 12 dias, atingiu 55 °C em 40 h: laudo **conforme**;
* LR-102 — montada há 5 dias, nunca passou de 52 °C: laudo **não conforme** e
  alerta crítico do motor;
* LR-103 — montada ontem, ainda aquecendo: ciclo **em andamento**, pronta
  para receber coletas ao vivo pelo PWA.

ATENÇÃO — só para demonstração: aferições de dias atrás violam a trava de 24h
(RF02), que o gatilho do banco aplica a qualquer cliente. Este script desliga
os gatilhos apenas dentro da própria transação (`SET LOCAL
session_replication_role = replica`, que exige o superusuário do PostgreSQL —
o usuário do docker-compose). Nenhum outro caminho do sistema consegue isso.

Os alertas são gerados pelo mesmo MotorDeAlertasService da API, sobre os
dados semeados — não são escritos à mão.

Uso (dentro do container, depois das migrations):
    docker compose exec api python -m scripts.seed_demo

Idempotente: se a usina de demonstração já existir, nada é feito.
"""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text

from app.application.services.motor_de_alertas_service import (
    MotorDeAlertasService,
    parametros_do_motor,
)
from app.domain.services.calculo_de_traco import ComponenteDaMistura, calcular_traco
from app.infrastructure.database.models.afericao import Afericao
from app.infrastructure.database.models.enums import PapelUsuario, StatusLeira
from app.infrastructure.database.models.leira import Leira
from app.infrastructure.database.models.leira_residuo import LeiraResiduo
from app.infrastructure.database.models.residuo import Residuo
from app.infrastructure.database.models.usina import Usina
from app.infrastructure.database.models.usuario import Usuario
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.afericao_repository_sqlalchemy import (
    AfericaoRepositorySQLAlchemy,
)
from app.infrastructure.repositories.alerta_repository_sqlalchemy import (
    AlertaRepositorySQLAlchemy,
)
from app.infrastructure.repositories.leira_repository_sqlalchemy import (
    LeiraRepositorySQLAlchemy,
)
from app.infrastructure.security.hash_bcrypt import HashDeSenhaBcrypt
from scripts.seed_residuos import semear as semear_residuos

NOME_DA_USINA = "Usina Vale Verde (demonstração)"

# Credenciais de teste da demonstração local — nunca usar em produção.
USUARIOS_DEMO = [
    ("Gestora Demo", "gestor@demo.aferra.local", "demo-gestor-2026", PapelUsuario.GESTOR),
    ("Operador Demo", "operador@demo.aferra.local", "demo-operador-2026", PapelUsuario.OPERADOR),
]

# Pátio da usina fictícia (região de Jaraguá do Sul/SC).
LATITUDE = Decimal("-26.486100")
LONGITUDE = Decimal("-49.066800")

# (código, dias desde a montagem, status, [(horas após a montagem, °C, umidade %)])
LEIRAS_DEMO = [
    (
        "LR-101",
        12,
        StatusLeira.ATIVA,
        [(6, "38.5"), (18, "46"), (30, "52.5"), (40, "57.5"), (64, "64.2"),
         (88, "62"), (136, "60.5"), (184, "58"), (232, "56.5"), (280, "54")],
    ),
    (
        "LR-102",
        5,
        StatusLeira.ATIVA,
        [(8, "36"), (24, "44.5"), (48, "51"), (70, "52"), (96, "49.5"), (110, "47")],
    ),
    ("LR-103", 1, StatusLeira.ATIVA, [(3, "34"), (12, "41.5"), (20, "47")]),
]

# Mistura usada nas três leiras (nome do resíduo do catálogo, massa em kg).
MISTURA = [("Esterco bovino", "620"), ("Restos de hortaliças", "180"), ("Serragem", "440")]


async def semear() -> None:
    await semear_residuos()

    async with SessionLocal() as session:
        if (
            await session.execute(select(Usina).where(Usina.nome == NOME_DA_USINA))
        ).scalar_one_or_none() is not None:
            print("Usina de demonstração já existe. Nada a fazer.")
            return

        # Só nesta transação: permite gravar o histórico de dias atrás (ver docstring).
        await session.execute(text("SET LOCAL session_replication_role = replica"))

        usina = Usina(nome=NOME_DA_USINA, latitude=LATITUDE, longitude=LONGITUDE)
        session.add(usina)
        await session.flush()

        hash_de_senha = HashDeSenhaBcrypt()
        usuarios = []
        for nome, email, senha, papel in USUARIOS_DEMO:
            usuario = Usuario(
                usina_id=usina.id,
                nome=nome,
                email=email,
                senha_hash=hash_de_senha.gerar_hash(senha),
                papel=papel,
            )
            session.add(usuario)
            usuarios.append(usuario)
        await session.flush()
        gestor, operador = usuarios

        residuos = {
            residuo.nome: residuo
            for residuo in (
                await session.execute(
                    select(Residuo).where(Residuo.nome.in_([nome for nome, _ in MISTURA]))
                )
            ).scalars()
        }
        traco = calcular_traco(
            [
                ComponenteDaMistura(
                    percentual_carbono=residuos[nome].percentual_carbono,
                    percentual_nitrogenio=residuos[nome].percentual_nitrogenio,
                    teor_umidade_percentual=residuos[nome].teor_umidade_percentual,
                    massa_kg=Decimal(massa),
                )
                for nome, massa in MISTURA
            ]
        )

        agora = datetime.now(UTC)
        leiras = []
        for codigo, dias, status, leituras in LEIRAS_DEMO:
            montagem = agora - timedelta(days=dias)
            leira = Leira(
                usina_id=usina.id,
                codigo=codigo,
                data_montagem=montagem,
                status=status,
                latitude=LATITUDE,
                longitude=LONGITUDE,
                relacao_cn_inicial=traco.relacao_cn,
                umidade_inicial_percentual=traco.umidade_percentual,
                massa_total_kg=traco.massa_total_kg,
                criado_por_id=gestor.id,
                observacoes="Leira de demonstração.",
            )
            session.add(leira)
            await session.flush()
            leiras.append(leira)

            for nome, massa in MISTURA:
                session.add(
                    LeiraResiduo(
                        leira_id=leira.id, residuo_id=residuos[nome].id, massa_kg=Decimal(massa)
                    )
                )
            for horas, temperatura in leituras:
                session.add(
                    Afericao(
                        leira_id=leira.id,
                        usuario_id=operador.id,
                        temperatura_celsius=Decimal(temperatura),
                        umidade_percentual=Decimal("55"),
                        registrado_em=montagem + timedelta(hours=horas),
                        # Pequena variação para as coordenadas não serem todas iguais.
                        latitude=LATITUDE + Decimal(horas % 7) / Decimal(100000),
                        longitude=LONGITUDE - Decimal(horas % 5) / Decimal(100000),
                        id_cliente=uuid.uuid4(),
                    )
                )
            await session.flush()

        # Alertas pelo motor real (RF03), com os mesmos parâmetros da API.
        motor = MotorDeAlertasService(
            LeiraRepositorySQLAlchemy(session),
            AfericaoRepositorySQLAlchemy(session),
            AlertaRepositorySQLAlchemy(session),
            parametros_do_motor(55.0, 72, 10.0),
        )
        total_de_alertas = 0
        for leira in leiras:
            total_de_alertas += len(await motor.avaliar_leira(leira.id))

        await session.commit()

    print(f"Usina de demonstração criada com {len(leiras)} leiras e {total_de_alertas} alertas.")
    print("Acessos de demonstração (somente ambiente local):")
    for nome, email, senha, papel in USUARIOS_DEMO:
        print(f"  {papel.value:<9} {email}  senha: {senha}")


if __name__ == "__main__":
    asyncio.run(semear())
