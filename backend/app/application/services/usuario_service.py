"""Casos de uso de Usuário (CRUD), incluindo o hash da senha na criação."""

from uuid import UUID

from app.application.dto.usuario import UsuarioAtualizar, UsuarioCriar, UsuarioResponse
from app.application.ports.repositorios import UsinaRepository, UsuarioRepository
from app.application.ports.seguranca import HashDeSenha
from app.domain.exceptions import EntidadeDuplicada, RecursoNaoEncontrado
from app.infrastructure.database.models.usuario import Usuario


class UsuarioService:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        usina_repo: UsinaRepository,
        hash_de_senha: HashDeSenha,
    ) -> None:
        self._repo = usuario_repo
        self._usina_repo = usina_repo
        self._hash = hash_de_senha

    async def criar(self, dados: UsuarioCriar) -> UsuarioResponse:
        if await self._usina_repo.obter_por_id(dados.usina_id) is None:
            raise RecursoNaoEncontrado("Usina informada não existe.")
        if await self._repo.obter_por_email(dados.email) is not None:
            raise EntidadeDuplicada("Já existe um usuário com esse e-mail.")

        usuario = Usuario(
            usina_id=dados.usina_id,
            nome=dados.nome,
            email=dados.email,
            senha_hash=self._hash.gerar_hash(dados.senha),
            papel=dados.papel,
        )
        usuario = await self._repo.adicionar(usuario)
        return UsuarioResponse.model_validate(usuario)

    async def listar(
        self, usina_id: UUID | None, limite: int, deslocamento: int
    ) -> list[UsuarioResponse]:
        usuarios = await self._repo.listar(usina_id, limite, deslocamento)
        return [UsuarioResponse.model_validate(u) for u in usuarios]

    async def obter(self, usuario_id: UUID) -> UsuarioResponse:
        return UsuarioResponse.model_validate(await self._obter_ou_falhar(usuario_id))

    async def atualizar(
        self, usuario_id: UUID, dados: UsuarioAtualizar
    ) -> UsuarioResponse:
        usuario = await self._obter_ou_falhar(usuario_id)
        alteracoes = dados.model_dump(exclude_unset=True)

        novo_email = alteracoes.pop("email", None)
        if novo_email is not None and novo_email != usuario.email:
            if await self._repo.obter_por_email(novo_email) is not None:
                raise EntidadeDuplicada("Já existe um usuário com esse e-mail.")
            usuario.email = novo_email

        nova_senha = alteracoes.pop("senha", None)
        if nova_senha is not None:
            usuario.senha_hash = self._hash.gerar_hash(nova_senha)

        for campo, valor in alteracoes.items():
            setattr(usuario, campo, valor)

        usuario = await self._repo.atualizar(usuario)
        return UsuarioResponse.model_validate(usuario)

    async def remover(self, usuario_id: UUID) -> None:
        usuario = await self._obter_ou_falhar(usuario_id)
        await self._repo.remover(usuario)

    async def _obter_ou_falhar(self, usuario_id: UUID) -> Usuario:
        usuario = await self._repo.obter_por_id(usuario_id)
        if usuario is None:
            raise RecursoNaoEncontrado("Usuário não encontrado.")
        return usuario
