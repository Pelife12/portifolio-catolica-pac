"""Testes unitários do caso de uso, sem passar pela camada HTTP."""

from app.application.use_cases.verificar_saude import VerificarSaudeUseCase
from app.domain.entities.status_saude import EstadoDependencia
from tests.conftest import VerificadorDeSaudeFake


async def test_sistema_operacional_quando_todas_dependencias_respondem():
    use_case = VerificarSaudeUseCase(VerificadorDeSaudeFake(disponivel=True))

    status = await use_case.executar()

    assert status.operacional is True
    assert status.banco_de_dados is EstadoDependencia.OPERACIONAL


async def test_sistema_degradado_quando_banco_esta_fora():
    use_case = VerificarSaudeUseCase(VerificadorDeSaudeFake(disponivel=False))

    status = await use_case.executar()

    assert status.operacional is False
    assert status.api is EstadoDependencia.OPERACIONAL
    assert status.banco_de_dados is EstadoDependencia.INDISPONIVEL
