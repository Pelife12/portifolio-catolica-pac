"""Rota de emissão do laudo em PDF (RF04)."""

from uuid import UUID

from fastapi import APIRouter, Response

from app.api.deps import LaudoServiceDep, UsuarioAtualDep

router = APIRouter(tags=["Laudos"])


@router.get(
    "/leiras/{leira_id}/laudo",
    response_class=Response,
    summary="Emite o laudo de rastreabilidade da leira em PDF",
    responses={200: {"content": {"application/pdf": {}}}},
)
async def emitir_laudo(
    leira_id: UUID, servico: LaudoServiceDep, usuario_atual: UsuarioAtualDep
) -> Response:
    # O emissor vem do token e fica registrado no laudo e no audit_log (RNF01).
    laudo = await servico.emitir(leira_id, usuario_atual.id, usuario_atual.nome)
    return Response(
        content=laudo.conteudo,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{laudo.nome_do_arquivo}"',
            "X-Laudo-Numero": laudo.numero,
            "X-Laudo-Hash": laudo.hash_de_integridade,
        },
    )
