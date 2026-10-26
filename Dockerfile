FROM python:3.12-slim as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./

RUN uv sync --no-install-project --no-dev

FROM python:3.12-slim 

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN useradd -m appuser 

WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000