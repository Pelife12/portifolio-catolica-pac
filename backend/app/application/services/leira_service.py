"""Casos de uso de Leira (CRUD).

O cálculo de traço (RF01) e o motor de alertas (RF03) atuam sobre a leira nas
entregas seguintes; aqui cobrimos o ciclo de vida básico do cadastro.
"""

from uuid import UUID

from app.application.dto.leira import LeiraAtualizar, LeiraCriar, LeiraResponse
from app.application.ports.repositorios import LeiraRepository, UsinaRepository
from app.domain.exceptions import EntidadeDuplicada, RecursoNaoEncontrado
from app.infrastructure.database.models.leira import Leira


class LeiraService:
    def __init__(
        self, leira_repo: LeiraRepository, usina_repo: UsinaRepository
    ) -> None:
        self._repo = leira_repo
        self._usina_repo = usina_repo

    async def criar(self, dados: LeiraCriar, criado_por_id: UUID) -> LeiraResponse:
        if await self._usina_repo.obter_por_id(dados.usina_id) is None:
            raise RecursoNaoEncontrado("Usina informada não existe.")
        if await self._repo.obter_por_codigo(dados.usina_id, dados.codigo) is not None:
            raise EntidadeDuplicada(
                "Já existe uma leira com esse código nesta usina."
            )

        leira = Leira(
            usina_id=dados.usina_id,
            codigo=dados.codigo,
            data_montagem=dados.data_montagem,
            latitude=dados.latitude,
            longitude=dados.longitude,
            observacoes=dados.observacoes,
            criado_por_id=criado_por_id,
        )
        leira = await self._repo.adicionar(leira)
        return LeiraResponse.model_validate(leira)

    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[LeiraResponse]:
        leiras = await self._repo.listar(usina_id, limite, deslocamento)
        return [LeiraResponse.model_validate(leira) for leira in leiras]

    async def obter(self, leira_id: UUID) -> LeiraResponse:
        return LeiraResponse.model_validate(await self._obter_ou_falhar(leira_id))

    async def atualizar(self, leira_id: UUID, dados: LeiraAtualizar) -> LeiraResponse:
        leira = await self._obter_ou_falhar(leira_id)
        alteracoes = dados.model_dump(exclude_unset=True)

        novo_codigo = alteracoes.get("codigo")
        if novo_codigo is not None and novo_codigo != leira.codigo:
            existente = await self._repo.obter_por_codigo(leira.usina_id, novo_codigo)
            if existente is not None:
                raise EntidadeDuplicada(
                    "Já existe uma leira com esse código nesta usina."
                )

        for campo, valor in alteracoes.items():
            setattr(leira, campo, valor)

        leira = await self._repo.atualizar(leira)
        return LeiraResponse.model_validate(leira)

    async def remover(self, leira_id: UUID) -> None:
        leira = await self._obter_ou_falhar(leira_id)
        await self._repo.remover(leira)

    async def _obter_ou_falhar(self, leira_id: UUID) -> Leira:
        leira = await self._repo.obter_por_id(leira_id)
        if leira is None:
            raise RecursoNaoEncontrado("Leira não encontrada.")
        return leira
