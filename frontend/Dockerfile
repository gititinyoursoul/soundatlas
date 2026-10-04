# syntax=docker/dockerfile:1

FROM node:24.11.1-bookworm-slim AS dev

ENV NODE_ENV=development \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 soundatlas \
    && useradd --uid 10001 --gid soundatlas --create-home --shell /bin/sh soundatlas \
    && mkdir -p /home/soundatlas/.npm

WORKDIR /workspace/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
RUN npx --no-install playwright install --with-deps chromium

COPY frontend/ ./
COPY data/seed/ /workspace/data/seed/
COPY docs/content/routes/ /workspace/docs/content/routes/
RUN chown -R soundatlas:soundatlas /workspace /home/soundatlas

USER 10001:10001
CMD ["sh", "-c", "if [ ! -x node_modules/.bin/vite ]; then npm ci; fi; npm run dev -- --host 0.0.0.0 --port 5173"]
