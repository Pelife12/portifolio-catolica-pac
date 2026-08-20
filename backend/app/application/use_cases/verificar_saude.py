"""Caso de uso: verificar a saúde da aplicação e de suas dependências."""

from app.domain.entities.status_saude import EstadoDependencia, StatusSaude
from app.domain.repositories.verificador_de_saude import VerificadorDeSaudeDoBanco


class VerificarSaudeUseCase:
    """Depende da abstração `VerificadorDeSaudeDoBanco`, nunca da implementação."""

    def __init__(self, verificador_do_banco: VerificadorDeSaudeDoBanco) -> None:
        self._verificador_do_banco = verificador_do_banco

    async def executar(self) -> StatusSaude:
        banco_disponivel = await self._verificador_do_banco.esta_disponivel()
        return StatusSaude(
            api=EstadoDependencia.OPERACIONAL,
            banco_de_dados=(
                EstadoDependencia.OPERACIONAL
                if banco_disponivel
                else EstadoDependencia.INDISPONIVEL
            ),
        )
