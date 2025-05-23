# Stage 1: Install dependencies
FROM docker.io/python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml .

RUN uv sync --no-dev --no-install-project --no-cache


# Stage 2: Start the application
FROM docker.io/python:3.13-alpine

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY . .

RUN adduser -D -g '' app && chown -R app:app ./

USER app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PATH="/opt/venv/bin:$PATH"

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --start-interval=2s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8080/api/health?format=json || exit 1

CMD [ "gunicorn", "config.wsgi", "--workers=8", "-b", "0.0.0.0:8080", "--access-logfile", "-", "--error-logfile", "-", "--timeout=600" ]
