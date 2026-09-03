"""Casos de uso de Aferição (RF02 + RNF01).

Aplica a trava temporal de 24h (regra pura do domínio), garante os dados de
auditoria (usuário autenticado + geolocalização, já exigidos pelo DTO) e trata a
sincronização idempotente do PWA: reenvios com o mesmo `id_cliente` não duplicam.
"""

from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.afericao import AfericaoCriar, AfericaoResponse
from app.application.ports.repositorios import AfericaoRepository, LeiraRepository
from app.domain.exceptions import RecursoNaoEncontrado
from app.domain.services.validacao_temporal import validar_janela_de_afericao
from app.infrastructure.database.models.afericao import Afericao


class AfericaoService:
    def __init__(
        self,
        afericao_repo: AfericaoRepository,
        leira_repo: LeiraRepository,
        janela_retroativa_horas: int,
    ) -> None:
        self._repo = afericao_repo
        self._leira_repo = leira_repo
        self._janela_horas = janela_retroativa_horas

    async def registrar(
        self, dados: AfericaoCriar, usuario_id: UUID
    ) -> tuple[AfericaoResponse, bool]:
        """Registra a aferição. Retorna (aferição, criada?).

        `criada` é False quando o `id_cliente` já havia sido sincronizado — o
        registro existente é devolvido, tornando o upload do PWA idempotente.
        """
        if dados.id_cliente is not None:
            existente = await self._repo.obter_por_id_cliente(dados.id_cliente)
            if existente is not None:
                return AfericaoResponse.model_validate(existente), False

        if await self._leira_repo.obter_por_id(dados.leira_id) is None:
            raise RecursoNaoEncontrado("Leira informada não existe.")

        # RF02: trava temporal (também reforçada por gatilho no banco).
        validar_janela_de_afericao(
            dados.registrado_em, agora=datetime.now(UTC), janela_horas=self._janela_horas
        )

        afericao = Afericao(
            leira_id=dados.leira_id,
            usuario_id=usuario_id,  # RNF01: sempre o usuário autenticado
            temperatura_celsius=dados.temperatura_celsius,
            umidade_percentual=dados.umidade_percentual,
            registrado_em=dados.registrado_em,
            latitude=dados.latitude,
            longitude=dados.longitude,
            id_cliente=dados.id_cliente,
        )
        afericao = await self._repo.adicionar(afericao)
        return AfericaoResponse.model_validate(afericao), True

    async def listar(
        self, leira_id: UUID | None, limite: int, deslocamento: int
    ) -> list[AfericaoResponse]:
        afericoes = await self._repo.listar(leira_id, limite, deslocamento)
        return [AfericaoResponse.model_validate(a) for a in afericoes]

    async def obter(self, afericao_id: UUID) -> AfericaoResponse:
        afericao = await self._repo.obter_por_id(afericao_id)
        if afericao is None:
            raise RecursoNaoEncontrado("Aferição não encontrada.")
        return AfericaoResponse.model_validate(afericao)
