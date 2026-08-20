"""Agregador das rotas da versão 1 da API."""

from fastapi import APIRouter

from app.api.v1.routes import auth, leiras, saude, usinas, usuarios

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(saude.router)
api_router.include_router(auth.router)
api_router.include_router(usinas.router)
api_router.include_router(usuarios.router)
api_router.include_router(leiras.router)
