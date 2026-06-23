# syntax=docker/dockerfile:1

FROM node:24.11.1-bookworm-slim AS node
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    CODEX_HOME=/home/soundatlas/.codex

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        gosu \
        iptables \
        less \
        procps \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 soundatlas \
    && useradd --uid 10001 --gid soundatlas --create-home --shell /bin/sh soundatlas \
    && mkdir -p /workspace /home/soundatlas/.cache/uv /home/soundatlas/.npm /home/soundatlas/.codex \
    && chown -R soundatlas:soundatlas /workspace /home/soundatlas

COPY docker/egress-guard.sh /usr/local/bin/egress-guard
RUN chmod 0755 /usr/local/bin/egress-guard

WORKDIR /workspace

ENTRYPOINT ["egress-guard"]
CMD ["sleep", "infinity"]
