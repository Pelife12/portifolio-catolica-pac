"""Testes do LaudoService (RF04): consolidação, hash e registro na auditoria."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.application.dto.laudo import DadosDoLaudo
from app.application.ports.relatorios import GeradorDeLaudo
from app.application.services.laudo_service import (
    LaudoService,
    calcular_hash_de_integridade,
)
from app.domain.exceptions import RecursoNaoEncontrado
from app.domain.services.conclusao_do_ciclo import SituacaoDoCiclo
from app.domain.services.motor_de_alertas import ParametrosDoMotor
from app.infrastructure.database.models.enums import AcaoAuditoria, StatusLeira

MONTAGEM = datetime.now(UTC) - timedelta(days=10)
OPERADOR_ID = uuid.uuid4()


def afericao(horas: float, temperatura: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        usuario_id=OPERADOR_ID,
        registrado_em=MONTAGEM + timedelta(hours=horas),
        temperatura_celsius=Decimal(temperatura),
        umidade_percentual=Decimal("55"),
        latitude=Decimal("-26.910000"),
        longitude=Decimal("-49.070000"),
    )


class Repo:
    """Dublê genérico: responde só aos métodos que o LaudoService usa."""

    def __init__(self, **respostas) -> None:
        self.__dict__.update(respostas)


class GeradorFalso(GeradorDeLaudo):
    def __init__(self) -> None:
        self.recebido: DadosDoLaudo | None = None

    def gerar(self, dados: DadosDoLaudo) -> bytes:
        self.recebido = dados
        return b"%PDF-falso"


class AuditoriaEmMemoria:
    def __init__(self) -> None:
        self.registros = []

    async def registrar(self, registro):
        self.registros.append(registro)
        return registro


def montar(leira, afericoes):
    async def obter_leira(_):
        return leira

    async def obter_usina(_):
        return SimpleNamespace(nome="Vale Verde", cnpj="12345678000190")

    async def obter_usuario(_):
        return SimpleNamespace(nome="Marina Duarte")

    async def listar_afericoes(*_):
        # O repositório real devolve do mais recente para o mais antigo.
        return sorted(afericoes, key=lambda a: a.registrado_em, reverse=True)

    async def vazio(*_):
        return []

    gerador = GeradorFalso()
    auditoria = AuditoriaEmMemoria()
    servico = LaudoService(
        leira_repo=Repo(obter_por_id=obter_leira),
        usina_repo=Repo(obter_por_id=obter_usina),
        usuario_repo=Repo(obter_por_id=obter_usuario),
        afericao_repo=Repo(listar=listar_afericoes),
        alerta_repo=Repo(listar=vazio),
        leira_residuo_repo=Repo(listar_por_leira=vazio),
        residuo_repo=Repo(obter_por_ids=vazio),
        auditoria_repo=auditoria,
        gerador=gerador,
        parametros=ParametrosDoMotor(),
    )
    return servico, gerador, auditoria


def nova_leira():
    return SimpleNamespace(
        id=uuid.uuid4(),
        usina_id=uuid.uuid4(),
        codigo="LR-014",
        data_montagem=MONTAGEM,
        status=StatusLeira.ATIVA,
        relacao_cn_inicial=Decimal("28.4"),
        umidade_inicial_percentual=Decimal("56"),
        massa_total_kg=Decimal("1240"),
    )


async def test_emite_laudo_conforme_com_historico_em_ordem_de_coleta():
    leira = nova_leira()
    historico = [afericao(60, "64.2"), afericao(12, "42"), afericao(40, "57.5")]
    servico, gerador, _ = montar(leira, historico)

    laudo = await servico.emitir(leira.id, uuid.uuid4(), "Gestor da usina")

    assert laudo.conteudo == b"%PDF-falso"
    assert laudo.nome_do_arquivo.startswith("laudo-LR-014-")
    dados = gerador.recebido
    assert dados.conclusao.situacao is SituacaoDoCiclo.CONFORME
    assert [a.temperatura_celsius for a in dados.afericoes] == [
        Decimal("42"),
        Decimal("57.5"),
        Decimal("64.2"),
    ]
    assert dados.afericoes[0].operador == "Marina Duarte"
    assert dados.emitido_por == "Gestor da usina"


async def test_registra_a_emissao_na_trilha_de_auditoria():
    leira = nova_leira()
    servico, _, auditoria = montar(leira, [afericao(40, "57")])
    emissor = uuid.uuid4()

    laudo = await servico.emitir(leira.id, emissor, "Gestor")

    (registro,) = auditoria.registros
    assert registro.acao is AcaoAuditoria.EXPORTAR_LAUDO
    assert registro.usuario_id == emissor
    assert registro.entidade_id == str(leira.id)
    assert registro.dados["hash_de_integridade"] == laudo.hash_de_integridade
    assert registro.dados["numero"] == laudo.numero


async def test_leira_inexistente():
    servico, _, auditoria = montar(None, [])

    with pytest.raises(RecursoNaoEncontrado):
        await servico.emitir(uuid.uuid4(), uuid.uuid4(), "Gestor")
    assert auditoria.registros == []


def test_hash_e_reproduzivel_e_sensivel_a_qualquer_alteracao():
    leira = nova_leira()
    historico = [afericao(12, "42"), afericao(40, "57.5")]

    original = calcular_hash_de_integridade(leira, historico)
    assert calcular_hash_de_integridade(leira, historico) == original

    adulterada = SimpleNamespace(**{**vars(historico[1]), "temperatura_celsius": Decimal("55.5")})
    assert calcular_hash_de_integridade(leira, [historico[0], adulterada]) != original
