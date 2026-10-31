"""Middlewares HTTP transversais.

RNF02: o sistema tem teto de 2 segundos por resposta. O medidor anota a duração
de toda requisição no cabeçalho padrão `Server-Timing` (visível no DevTools e no
PWA) e registra um aviso quando o teto é ultrapassado, para a rota lenta
aparecer no log antes de virar reclamação do pátio.
"""

import logging
import time

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("app.desempenho")


def registrar_medidor_de_tempo(app: FastAPI, teto_ms: int) -> None:
    @app.middleware("http")
    async def medir_tempo_de_resposta(request: Request, call_next) -> Response:
        inicio = time.perf_counter()
        resposta: Response = await call_next(request)
        decorrido_ms = (time.perf_counter() - inicio) * 1000

        resposta.headers["Server-Timing"] = f"app;dur={decorrido_ms:.1f}"
        if decorrido_ms > teto_ms:
            logger.warning(
                "RNF02: %s %s levou %.0f ms (teto de %d ms).",
                request.method,
                request.url.path,
                decorrido_ms,
                teto_ms,
            )
        return resposta
