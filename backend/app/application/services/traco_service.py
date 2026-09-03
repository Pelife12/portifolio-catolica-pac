"""Serviço de cálculo de traço (RF01): orquestra o domínio e a persistência.

Resolve os resíduos informados, delega o cálculo à regra pura do domínio
(`calcular_traco`) e, na definição da composição, persiste os itens e grava o
traço inicial na leira.
"""

from uuid import UUID

from app.application.dto.leira import LeiraResponse
from app.application.dto.traco import (
    ComposicaoItemResponse,
    ItemComposicao,
    ResultadoTracoResponse,
)
from app.application.ports.repositorios import (
    LeiraRepository,
    LeiraResiduoRepository,
    ResiduoRepository,
)
from app.domain.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from app.domain.services.calculo_de_traco import (
    ComponenteDaMistura,
    ResultadoDoTraco,
    calcular_traco,
)
from app.infrastructure.database.models.residuo import Residuo


class TracoService:
    def __init__(
        self,
        residuo_repo: ResiduoRepository,
        leira_repo: LeiraRepository,
        leira_residuo_repo: LeiraResiduoRepository,
    ) -> None:
        self._residuo_repo = residuo_repo
        self._leira_repo = leira_repo
        self._leira_residuo_repo = leira_residuo_repo

    async def calcular(self, itens: list[ItemComposicao]) -> ResultadoTracoResponse:
        resultado = await self._calcular_traco(itens)
        return self._para_response(resultado)

    async def definir_composicao(
        self, leira_id: UUID, itens: list[ItemComposicao]
    ) -> LeiraResponse:
        leira = await self._leira_repo.obter_por_id(leira_id)
        if leira is None:
            raise RecursoNaoEncontrado("Leira não encontrada.")

        resultado = await self._calcular_traco(itens)

        await self._leira_residuo_repo.substituir_composicao(
            leira_id, [(item.residuo_id, item.massa_kg) for item in itens]
        )

        # Grava o traço inicial na leira (RF01: "no momento da criação da leira").
        leira.relacao_cn_inicial = resultado.relacao_cn
        leira.umidade_inicial_percentual = resultado.umidade_percentual
        leira.massa_total_kg = resultado.massa_total_kg
        leira = await self._leira_repo.atualizar(leira)

        return LeiraResponse.model_validate(leira)

    async def listar_composicao(self, leira_id: UUID) -> list[ComposicaoItemResponse]:
        leira = await self._leira_repo.obter_por_id(leira_id)
        if leira is None:
            raise RecursoNaoEncontrado("Leira não encontrada.")

        itens = await self._leira_residuo_repo.listar_por_leira(leira_id)
        residuos = {
            r.id: r
            for r in await self._residuo_repo.obter_por_ids([i.residuo_id for i in itens])
        }
        return [
            ComposicaoItemResponse(
                residuo_id=item.residuo_id,
                residuo_nome=residuos[item.residuo_id].nome,
                massa_kg=item.massa_kg,
            )
            for item in itens
        ]

    # ------------------------------------------------------------------
    async def _calcular_traco(self, itens: list[ItemComposicao]) -> ResultadoDoTraco:
        ids = [item.residuo_id for item in itens]
        if len(set(ids)) != len(ids):
            raise RegraDeNegocioViolada(
                "Resíduo repetido na composição; some as massas em um único item."
            )

        residuos = {r.id: r for r in await self._residuo_repo.obter_por_ids(ids)}
        faltando = [str(i) for i in ids if i not in residuos]
        if faltando:
            raise RecursoNaoEncontrado(
                f"Resíduo(s) não encontrado(s): {', '.join(faltando)}."
            )

        componentes = [
            self._para_componente(residuos[item.residuo_id], item) for item in itens
        ]
        return calcular_traco(componentes)

    @staticmethod
    def _para_componente(residuo: Residuo, item: ItemComposicao) -> ComponenteDaMistura:
        if not residuo.ativo:
            raise RegraDeNegocioViolada(
                f"O resíduo '{residuo.nome}' está inativo e não pode ser usado."
            )
        return ComponenteDaMistura(
            percentual_carbono=residuo.percentual_carbono,
            percentual_nitrogenio=residuo.percentual_nitrogenio,
            teor_umidade_percentual=residuo.teor_umidade_percentual,
            massa_kg=item.massa_kg,
        )

    @staticmethod
    def _para_response(resultado: ResultadoDoTraco) -> ResultadoTracoResponse:
        return ResultadoTracoResponse(
            massa_total_kg=resultado.massa_total_kg,
            massa_seca_kg=resultado.massa_seca_kg,
            carbono_total_kg=resultado.carbono_total_kg,
            nitrogenio_total_kg=resultado.nitrogenio_total_kg,
            relacao_cn=resultado.relacao_cn,
            umidade_percentual=resultado.umidade_percentual,
            cn_dentro_do_ideal=resultado.cn_dentro_do_ideal,
            umidade_dentro_do_ideal=resultado.umidade_dentro_do_ideal,
        )
