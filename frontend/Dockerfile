# syntax=docker/dockerfile:1

FROM node:24.11.1-bookworm-slim

ENV NODE_ENV=development

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gosu \
        iptables \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 soundatlas \
    && useradd --uid 10001 --gid soundatlas --create-home --shell /usr/sbin/nologin soundatlas

WORKDIR /workspace/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY docker/egress-guard.sh /usr/local/bin/egress-guard
RUN chmod 0755 /usr/local/bin/egress-guard

COPY frontend/ ./
RUN chown -R soundatlas:soundatlas /workspace /home/soundatlas

ENTRYPOINT ["egress-guard"]
CMD ["sh", "-c", "if [ ! -x node_modules/.bin/vite ]; then npm ci; fi; npm run dev -- --host 0.0.0.0 --port 5173"]
