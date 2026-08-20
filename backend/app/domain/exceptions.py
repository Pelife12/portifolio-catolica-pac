"""Exceções de negócio do domínio.

São traduzidas para respostas HTTP na camada de API (app/api/error_handlers.py),
de modo que o domínio permanece independente do framework web.
"""


class ErroDeDominio(Exception):
    """Raiz de todas as violações de regra de negócio do sistema."""

    mensagem_padrao = "Violação de regra de negócio."

    def __init__(self, mensagem: str | None = None) -> None:
        self.mensagem = mensagem or self.mensagem_padrao
        super().__init__(self.mensagem)


class RecursoNaoEncontrado(ErroDeDominio):
    mensagem_padrao = "Recurso não encontrado."


class RegraDeNegocioViolada(ErroDeDominio):
    mensagem_padrao = "A operação viola uma regra de negócio."


class ServicoIndisponivel(ErroDeDominio):
    """Dependência externa essencial (ex.: banco de dados) fora do ar."""

    mensagem_padrao = "Serviço temporariamente indisponível."
