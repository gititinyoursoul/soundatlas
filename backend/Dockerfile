# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/workspace/backend/.venv \
    PATH="/workspace/backend/.venv/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gosu \
        iptables \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 soundatlas \
    && useradd --uid 10001 --gid soundatlas --create-home --shell /usr/sbin/nologin soundatlas

WORKDIR /workspace/backend

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --frozen

COPY docker/egress-guard.sh /usr/local/bin/egress-guard
RUN chmod 0755 /usr/local/bin/egress-guard

COPY backend/ ./
RUN chown -R soundatlas:soundatlas /workspace /home/soundatlas

ENTRYPOINT ["egress-guard"]
CMD ["sh", "-c", "uv sync --frozen && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"]
