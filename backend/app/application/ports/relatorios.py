"""Porta de geração de documentos (RF04)."""

from abc import ABC, abstractmethod

from app.application.dto.laudo import DadosDoLaudo


class GeradorDeLaudo(ABC):
    @abstractmethod
    def gerar(self, dados: DadosDoLaudo) -> bytes:
        """Devolve o documento pronto (PDF) a partir dos dados já consolidados."""
