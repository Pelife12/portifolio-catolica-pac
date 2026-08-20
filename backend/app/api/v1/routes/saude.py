"""Endpoint de health-check da API."""

from fastapi import APIRouter, Response, status

from app.api.deps import SettingsDep, VerificarSaudeUseCaseDep
from app.api.schemas.saude import SaudeResponse

router = APIRouter(tags=["Saúde"])


@router.get(
    "/saude",
    response_model=SaudeResponse,
    summary="Verifica a disponibilidade da API e do banco de dados",
)
async def verificar_saude(
    use_case: VerificarSaudeUseCaseDep,
    settings: SettingsDep,
    response: Response,
) -> SaudeResponse:
    status_saude = await use_case.executar()

    if not status_saude.operacional:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return SaudeResponse(
        status="operacional" if status_saude.operacional else "degradado",
        api=status_saude.api.value,
        banco_de_dados=status_saude.banco_de_dados.value,
        versao=settings.versao_app,
        ambiente=settings.ambiente,
    )
