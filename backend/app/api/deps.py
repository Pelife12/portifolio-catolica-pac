"""Composition root: aqui as dependências concretas são injetadas nos casos de uso.

Este é o único ponto onde a camada de API conhece a infraestrutura. Os casos de
uso continuam recebendo apenas abstrações do domínio.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.verificar_saude import VerificarSaudeUseCase
from app.domain.repositories.verificador_de_saude import VerificadorDeSaudeDoBanco
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.session import get_session
from app.infrastructure.database.verificador_de_saude_postgres import VerificadorDeSaudePostgres

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_verificador_de_saude(session: SessionDep) -> VerificadorDeSaudeDoBanco:
    return VerificadorDeSaudePostgres(session)


def get_verificar_saude_use_case(
    verificador: Annotated[VerificadorDeSaudeDoBanco, Depends(get_verificador_de_saude)],
) -> VerificarSaudeUseCase:
    return VerificarSaudeUseCase(verificador)


VerificarSaudeUseCaseDep = Annotated[
    VerificarSaudeUseCase, Depends(get_verificar_saude_use_case)
]
