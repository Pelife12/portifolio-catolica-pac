"""Agregador das rotas da versão 1 da API."""

from fastapi import APIRouter

from app.api.v1.routes import saude

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
