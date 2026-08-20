"""Serviço de autenticação: valida credenciais e emite o token de acesso."""

from app.application.dto.autenticacao import TokenResponse
from app.application.ports.repositorios import UsuarioRepository
from app.application.ports.seguranca import GeradorDeToken, HashDeSenha
from app.domain.exceptions import CredenciaisInvalidas


class AutenticacaoService:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        hash_de_senha: HashDeSenha,
        gerador_de_token: GeradorDeToken,
    ) -> None:
        self._usuario_repo = usuario_repo
        self._hash = hash_de_senha
        self._token = gerador_de_token

    async def autenticar(self, email: str, senha: str) -> TokenResponse:
        usuario = await self._usuario_repo.obter_por_email(email)

        # Mesma resposta para e-mail inexistente ou senha errada: não revela
        # quais e-mails estão cadastrados. A verificação do hash roda de todo
        # modo apenas quando há usuário (evita custo desnecessário).
        if usuario is None or not self._hash.verificar(senha, usuario.senha_hash):
            raise CredenciaisInvalidas()

        if not usuario.ativo:
            raise CredenciaisInvalidas("Usuário inativo.")

        token = self._token.gerar_token_de_acesso(usuario.id, usuario.papel.value)
        return TokenResponse(
            access_token=token,
            expira_em_segundos=self._token.expira_em_segundos,
        )
