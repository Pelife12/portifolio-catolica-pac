"""RF01 — Cálculo de traço da leira.

Regra de negócio pura: a partir das massas dos resíduos e de seus parâmetros
agronômicos (percentual de carbono e de nitrogênio em base seca e teor de
umidade), calcula a relação Carbono/Nitrogênio (C/N) e a umidade resultantes da
mistura, e diagnostica se caem nas faixas ideais para compostagem.

Fundamentos do cálculo:
* cada resíduo entra com massa ÚMIDA; a fração de água é `massa * umidade%`;
* carbono e nitrogênio são medidos em BASE SECA, então incidem sobre a massa
  seca (massa úmida menos a água);
* C/N = carbono total / nitrogênio total (ambos em kg de massa seca);
* umidade da mistura = água total / massa úmida total.

Este módulo não conhece banco nem HTTP — é a base de conhecimento do sistema e
o alvo dos testes unitários da entrega.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.exceptions import RegraDeNegocioViolada

# Faixas ideais para a compostagem (base de conhecimento agronômica).
CN_IDEAL_MINIMO = Decimal("25")
CN_IDEAL_MAXIMO = Decimal("35")
UMIDADE_IDEAL_MINIMA = Decimal("50")
UMIDADE_IDEAL_MAXIMA = Decimal("60")

_CEM = Decimal("100")


@dataclass(frozen=True)
class ComponenteDaMistura:
    """Um resíduo e sua massa dentro da mistura da leira."""

    percentual_carbono: Decimal      # % em base seca
    percentual_nitrogenio: Decimal   # % em base seca
    teor_umidade_percentual: Decimal  # % da massa úmida
    massa_kg: Decimal


@dataclass(frozen=True)
class ResultadoDoTraco:
    massa_total_kg: Decimal
    massa_seca_kg: Decimal
    carbono_total_kg: Decimal
    nitrogenio_total_kg: Decimal
    relacao_cn: Decimal
    umidade_percentual: Decimal
    cn_dentro_do_ideal: bool
    umidade_dentro_do_ideal: bool


def _arredondar(valor: Decimal, casas: int) -> Decimal:
    return valor.quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)


def calcular_traco(componentes: Sequence[ComponenteDaMistura]) -> ResultadoDoTraco:
    """Calcula o traço da mistura. Lança RegraDeNegocioViolada em entradas inválidas."""
    if not componentes:
        raise RegraDeNegocioViolada(
            "Informe ao menos um resíduo para calcular o traço."
        )

    massa_total = Decimal("0")
    massa_agua = Decimal("0")
    massa_seca = Decimal("0")
    carbono = Decimal("0")
    nitrogenio = Decimal("0")

    for c in componentes:
        if c.massa_kg <= 0:
            raise RegraDeNegocioViolada("A massa de cada resíduo deve ser positiva.")

        agua = c.massa_kg * c.teor_umidade_percentual / _CEM
        seca = c.massa_kg - agua
        massa_total += c.massa_kg
        massa_agua += agua
        massa_seca += seca
        carbono += seca * c.percentual_carbono / _CEM
        nitrogenio += seca * c.percentual_nitrogenio / _CEM

    if nitrogenio <= 0:
        raise RegraDeNegocioViolada(
            "A mistura não possui nitrogênio; adicione resíduos ricos em nitrogênio "
            "(verdes) para viabilizar o cálculo da relação C/N."
        )

    relacao_cn = carbono / nitrogenio
    umidade = massa_agua / massa_total * _CEM

    return ResultadoDoTraco(
        massa_total_kg=_arredondar(massa_total, 3),
        massa_seca_kg=_arredondar(massa_seca, 3),
        carbono_total_kg=_arredondar(carbono, 3),
        nitrogenio_total_kg=_arredondar(nitrogenio, 3),
        relacao_cn=_arredondar(relacao_cn, 2),
        umidade_percentual=_arredondar(umidade, 2),
        cn_dentro_do_ideal=CN_IDEAL_MINIMO <= relacao_cn <= CN_IDEAL_MAXIMO,
        umidade_dentro_do_ideal=UMIDADE_IDEAL_MINIMA <= umidade <= UMIDADE_IDEAL_MAXIMA,
    )
