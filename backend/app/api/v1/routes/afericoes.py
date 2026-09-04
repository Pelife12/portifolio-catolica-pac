"""Rotas de Aferição (RF02 + RNF01), todas exigem autenticação."""

from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.deps import AfericaoServiceDep, MotorServiceDep, UsuarioAtualDep
from app.application.dto.afericao import AfericaoCriar, AfericaoResponse

router = APIRouter(prefix="/afericoes", tags=["Aferições"])


@router.post("", response_model=AfericaoResponse)
async def registrar_afericao(
    dados: AfericaoCriar,
    servico: AfericaoServiceDep,
    motor: MotorServiceDep,
    usuario_atual: UsuarioAtualDep,
    response: Response,
) -> AfericaoResponse:
    # O usuário vem do token (RNF01), nunca do corpo da requisição.
    afericao, criada = await servico.registrar(dados, usuario_id=usuario_atual.id)
    # 201 quando registrada; 200 quando o id_cliente já existia (idempotência).
    response.status_code = status.HTTP_201_CREATED if criada else status.HTTP_200_OK
    # RF03: só reavalia a leira quando a coleta é nova (evita retrabalho em reenvios).
    if criada:
        await motor.avaliar_leira(afericao.leira_id)
    return afericao


@router.get("", response_model=list[AfericaoResponse])
async def listar_afericoes(
    servico: AfericaoServiceDep,
    _: UsuarioAtualDep,
    leira_id: UUID | None = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    deslocamento: int = Query(default=0, ge=0),
) -> list[AfericaoResponse]:
    return await servico.listar(leira_id, limite, deslocamento)


@router.get("/{afericao_id}", response_model=AfericaoResponse)
async def obter_afericao(
    afericao_id: UUID, servico: AfericaoServiceDep, _: UsuarioAtualDep
) -> AfericaoResponse:
    return await servico.obter(afericao_id)
