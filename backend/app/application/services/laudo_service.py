"""RF04 — Emissão do laudo de rastreabilidade do lote.

Consolida tudo o que o auditor precisa ver sobre uma leira — identificação,
traço inicial, histórico de aferições com a trilha de auditoria (quem, quando e
onde), alertas do motor e a conclusão do ciclo termofílico — e entrega ao
gerador de PDF. A emissão é registrada no audit_log com o número e o hash do
laudo, para qualquer cópia poder ser conferida depois.
"""

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.laudo import (
    AfericaoDoLaudo,
    AlertaDoLaudo,
    DadosDoLaudo,
    ItemDaComposicaoDoLaudo,
    LaudoEmitido,
)
from app.application.ports.relatorios import GeradorDeLaudo
from app.application.ports.repositorios import (
    AfericaoRepository,
    AlertaRepository,
    AuditoriaRepository,
    LeiraRepository,
    LeiraResiduoRepository,
    ResiduoRepository,
    UsinaRepository,
    UsuarioRepository,
)
from app.domain.exceptions import RecursoNaoEncontrado
from app.domain.services.conclusao_do_ciclo import concluir_ciclo
from app.domain.services.motor_de_alertas import LeituraDeTemperatura, ParametrosDoMotor
from app.infrastructure.database.models.audit_log import AuditLog
from app.infrastructure.database.models.enums import AcaoAuditoria

# Teto defensivo do histórico de uma leira no laudo (um ciclo tem dezenas de leituras).
_LIMITE_HISTORICO = 5000


class LaudoService:
    def __init__(
        self,
        leira_repo: LeiraRepository,
        usina_repo: UsinaRepository,
        usuario_repo: UsuarioRepository,
        afericao_repo: AfericaoRepository,
        alerta_repo: AlertaRepository,
        leira_residuo_repo: LeiraResiduoRepository,
        residuo_repo: ResiduoRepository,
        auditoria_repo: AuditoriaRepository,
        gerador: GeradorDeLaudo,
        parametros: ParametrosDoMotor,
    ) -> None:
        self._leira_repo = leira_repo
        self._usina_repo = usina_repo
        self._usuario_repo = usuario_repo
        self._afericao_repo = afericao_repo
        self._alerta_repo = alerta_repo
        self._leira_residuo_repo = leira_residuo_repo
        self._residuo_repo = residuo_repo
        self._auditoria_repo = auditoria_repo
        self._gerador = gerador
        self._parametros = parametros

    async def emitir(
        self, leira_id: UUID, emitido_por_id: UUID, emitido_por_nome: str
    ) -> LaudoEmitido:
        leira = await self._leira_repo.obter_por_id(leira_id)
        if leira is None:
            raise RecursoNaoEncontrado("Leira não encontrada.")
        usina = await self._usina_repo.obter_por_id(leira.usina_id)

        afericoes = sorted(
            await self._afericao_repo.listar(leira_id, _LIMITE_HISTORICO, 0),
            # Desempate pelo id: a ordem precisa ser estável para o hash ser reproduzível.
            key=lambda afericao: (afericao.registrado_em, str(afericao.id)),
        )
        alertas = await self._alerta_repo.listar(leira_id, None, _LIMITE_HISTORICO, 0)
        composicao = await self._leira_residuo_repo.listar_por_leira(leira_id)
        residuos = {
            residuo.id: residuo
            for residuo in await self._residuo_repo.obter_por_ids(
                [item.residuo_id for item in composicao]
            )
        }
        operadores = await self._nomes_dos_operadores({a.usuario_id for a in afericoes})

        agora = datetime.now(UTC)
        conclusao = concluir_ciclo(
            leira.data_montagem,
            [
                LeituraDeTemperatura(
                    afericao_id=a.id,
                    registrado_em=a.registrado_em,
                    temperatura_celsius=a.temperatura_celsius,
                )
                for a in afericoes
            ],
            agora,
            self._parametros,
        )

        hash_de_integridade = calcular_hash_de_integridade(leira, afericoes)
        numero = f"{agora:%Y-%m%d}-{leira.codigo}-{hash_de_integridade[:6].upper()}"

        dados = DadosDoLaudo(
            numero=numero,
            emitido_em=agora,
            emitido_por=emitido_por_nome,
            usina=usina.nome if usina else "—",
            usina_cnpj=usina.cnpj if usina else None,
            leira_codigo=leira.codigo,
            data_montagem=leira.data_montagem,
            status_da_leira=leira.status.value,
            relacao_cn_inicial=leira.relacao_cn_inicial,
            umidade_inicial_percentual=leira.umidade_inicial_percentual,
            massa_total_kg=leira.massa_total_kg,
            temperatura_minima=self._parametros.temperatura_minima,
            prazo_termofilico_horas=self._parametros.prazo_termofilico_horas,
            conclusao=conclusao,
            composicao=[
                ItemDaComposicaoDoLaudo(
                    residuo=residuos[item.residuo_id].nome
                    if item.residuo_id in residuos
                    else "Resíduo removido",
                    massa_kg=item.massa_kg,
                )
                for item in composicao
            ],
            afericoes=[
                AfericaoDoLaudo(
                    registrado_em=a.registrado_em,
                    temperatura_celsius=a.temperatura_celsius,
                    umidade_percentual=a.umidade_percentual,
                    operador=operadores.get(a.usuario_id, "—"),
                    latitude=a.latitude,
                    longitude=a.longitude,
                )
                for a in afericoes
            ],
            alertas=[
                AlertaDoLaudo(
                    tipo=alerta.tipo.value,
                    severidade=alerta.severidade.value,
                    status=alerta.status.value,
                    mensagem=alerta.mensagem,
                    detectado_em=alerta.detectado_em,
                )
                for alerta in sorted(alertas, key=lambda alerta: alerta.detectado_em)
            ],
            hash_de_integridade=hash_de_integridade,
        )

        # Montar o PDF é trabalho de CPU: roda fora do loop para não travar a API.
        conteudo = await asyncio.to_thread(self._gerador.gerar, dados)

        await self._auditoria_repo.registrar(
            AuditLog(
                usuario_id=emitido_por_id,
                acao=AcaoAuditoria.EXPORTAR_LAUDO,
                entidade="leira",
                entidade_id=str(leira_id),
                dados={
                    "numero": numero,
                    "hash_de_integridade": hash_de_integridade,
                    "situacao": conclusao.situacao.value,
                    "total_de_afericoes": len(afericoes),
                },
            )
        )

        return LaudoEmitido(
            numero=numero,
            nome_do_arquivo=f"laudo-{leira.codigo}-{agora:%Y%m%d}.pdf",
            conteudo=conteudo,
            hash_de_integridade=hash_de_integridade,
        )

    async def _nomes_dos_operadores(self, ids: set[UUID]) -> dict[UUID, str]:
        nomes: dict[UUID, str] = {}
        for usuario_id in ids:
            usuario = await self._usuario_repo.obter_por_id(usuario_id)
            nomes[usuario_id] = usuario.nome if usuario else "Usuário removido"
        return nomes


def calcular_hash_de_integridade(leira, afericoes) -> str:
    """SHA-256 dos dados de origem do laudo, em JSON canônico.

    Depende só do que foi coletado (não do momento da emissão): dois laudos da
    mesma leira com o mesmo histórico têm o mesmo hash, e qualquer alteração em
    uma aferição — valor, horário, coordenada ou autor — muda o resultado.
    """
    payload = {
        "leira": {
            "id": str(leira.id),
            "codigo": leira.codigo,
            "data_montagem": leira.data_montagem.isoformat(),
        },
        "afericoes": [
            {
                "id": str(a.id),
                "registrado_em": a.registrado_em.isoformat(),
                "temperatura_celsius": str(a.temperatura_celsius),
                "umidade_percentual": None
                if a.umidade_percentual is None
                else str(a.umidade_percentual),
                "latitude": str(a.latitude),
                "longitude": str(a.longitude),
                "usuario_id": str(a.usuario_id),
            }
            for a in afericoes
        ],
    }
    canonico = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()
