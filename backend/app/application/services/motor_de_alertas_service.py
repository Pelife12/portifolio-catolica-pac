"""Serviço do motor de alertas (RF03): avalia uma leira e grava as anomalias.

Carrega o histórico de aferições, delega a inferência à regra pura do domínio e
persiste os alertas novos — sem duplicar os que já existem para a mesma leira
(mesmo tipo e, quando aplicável, mesma aferição de origem).
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from app.application.dto.alerta import AlertaResponse
from app.application.ports.repositorios import (
    AfericaoRepository,
    AlertaRepository,
    LeiraRepository,
)
from app.domain.exceptions import RecursoNaoEncontrado
from app.domain.services.motor_de_alertas import (
    LeituraDeTemperatura,
    ParametrosDoMotor,
    avaliar_leira,
)
from app.infrastructure.database.models.alerta import Alerta
from app.infrastructure.database.models.enums import (
    SeveridadeAlerta,
    StatusAlerta,
    TipoAlerta,
)

# Teto defensivo para o histórico avaliado por vez.
_LIMITE_HISTORICO = 5000


class MotorDeAlertasService:
    def __init__(
        self,
        leira_repo: LeiraRepository,
        afericao_repo: AfericaoRepository,
        alerta_repo: AlertaRepository,
        parametros: ParametrosDoMotor,
    ) -> None:
        self._leira_repo = leira_repo
        self._afericao_repo = afericao_repo
        self._alerta_repo = alerta_repo
        self._parametros = parametros

    async def avaliar_leira(self, leira_id: UUID) -> list[AlertaResponse]:
        leira = await self._leira_repo.obter_por_id(leira_id)
        if leira is None:
            raise RecursoNaoEncontrado("Leira não encontrada.")

        afericoes = await self._afericao_repo.listar(leira_id, _LIMITE_HISTORICO, 0)
        leituras = [
            LeituraDeTemperatura(
                afericao_id=a.id,
                registrado_em=a.registrado_em,
                temperatura_celsius=a.temperatura_celsius,
            )
            for a in afericoes
        ]

        anomalias = avaliar_leira(
            leira.data_montagem, leituras, datetime.now(UTC), self._parametros
        )

        criados: list[Alerta] = []
        for anomalia in anomalias:
            tipo = TipoAlerta(anomalia.tipo.value)
            if await self._alerta_repo.existe_para(leira_id, tipo, anomalia.afericao_id):
                continue
            alerta = Alerta(
                leira_id=leira_id,
                afericao_id=anomalia.afericao_id,
                tipo=tipo,
                severidade=SeveridadeAlerta(anomalia.severidade.value),
                status=StatusAlerta.ABERTO,
                mensagem=anomalia.mensagem,
                detectado_em=anomalia.detectado_em,
            )
            criados.append(await self._alerta_repo.adicionar(alerta))

        return [AlertaResponse.model_validate(a) for a in criados]


def parametros_do_motor(
    temperatura_minima: float, prazo_horas: int, queda_brusca_delta: float
) -> ParametrosDoMotor:
    """Converte a configuração (float) nos parâmetros do domínio (Decimal)."""
    return ParametrosDoMotor(
        temperatura_minima=Decimal(str(temperatura_minima)),
        prazo_termofilico_horas=prazo_horas,
        queda_brusca_delta=Decimal(str(queda_brusca_delta)),
    )
