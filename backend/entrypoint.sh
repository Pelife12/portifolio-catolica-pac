#!/usr/bin/env bash
# Aplica as migrations pendentes e sobe a API. O banco é sempre levado ao estado
# descrito pelos modelos Python antes de a aplicação começar a atender.
set -e

echo "Aplicando migrations (alembic upgrade head)..."
alembic upgrade head

echo "Iniciando a API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
