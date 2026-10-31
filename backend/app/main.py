"""Ponto de entrada da aplicação FastAPI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import registrar_error_handlers
from app.api.middlewares import registrar_medidor_de_tempo
from app.api.v1.router import api_router
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    logger.info("Iniciando %s (ambiente=%s)", settings.nome_app, settings.ambiente)
    yield
    await engine.dispose()
    logger.info("Conexões com o banco encerradas.")


def criar_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.nome_app,
        version=settings.versao_app,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origens_permitidas,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Cabeçalhos lidos pelo PWA: duração da resposta (RNF02) e dados do laudo (RF04).
        expose_headers=["Server-Timing", "Content-Disposition", "X-Laudo-Numero", "X-Laudo-Hash"],
    )

    registrar_medidor_de_tempo(app, settings.teto_tempo_resposta_ms)
    registrar_error_handlers(app)
    app.include_router(api_router)

    return app


app = criar_app()
