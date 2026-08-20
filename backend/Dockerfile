FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && pip install -r requirements-dev.txt

COPY . .

RUN chmod +x entrypoint.sh \
    && useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Aplica as migrations e então sobe a API (ver entrypoint.sh).
CMD ["./entrypoint.sh"]
