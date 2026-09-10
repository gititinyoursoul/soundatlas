# syntax=docker/dockerfile:1

FROM node:24.11.1-bookworm-slim AS node
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS soundatlas-tooling

ARG CODEX_CLI_VERSION=0.147.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    CODEX_HOME=/home/soundatlas/.codex \
    GH_CONFIG_DIR=/home/soundatlas/.config/gh

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -sf ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        bash-completion \
        bubblewrap \
        ca-certificates \
        curl \
        fonts-liberation \
        git \
        gosu \
        iptables \
        jq \
        less \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libx11-6 \
        libxcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxkbcommon0 \
        libxrandr2 \
        procps \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g "@openai/codex@${CODEX_CLI_VERSION}"

RUN groupadd --gid 10001 soundatlas \
    && useradd --uid 10001 --gid soundatlas --create-home --shell /bin/bash soundatlas \
    && mkdir -p /workspace /home/soundatlas/.cache/ms-playwright /home/soundatlas/.cache/uv /home/soundatlas/.config/gh /home/soundatlas/.npm /home/soundatlas/.codex \
    && chown -R soundatlas:soundatlas /workspace /home/soundatlas

COPY .devcontainer/bashrc /home/soundatlas/.bashrc
RUN chown soundatlas:soundatlas /home/soundatlas/.bashrc

COPY docker/egress-guard.sh /usr/local/bin/egress-guard
RUN chmod 0755 /usr/local/bin/egress-guard

FROM soundatlas-tooling AS workspace

WORKDIR /workspace
ENTRYPOINT ["egress-guard"]
CMD ["sleep", "infinity"]

FROM soundatlas-tooling AS pane-workspace

ARG PANE_VERSION=2.4.102
ARG PANE_SHA256=5e7155c9eb96aebbc575166ce26318c0475d2b26bf6df0dc5943c371deda594f
ARG PANE_NPM_VERSION=11.19.1
ARG PANE_CODEX_CLI_VERSION=0.154.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && curl -fsSLo /tmp/pane.deb "https://github.com/dcouple/Pane/releases/download/v${PANE_VERSION}/Pane-${PANE_VERSION}-linux-amd64.deb" \
    && echo "${PANE_SHA256}  /tmp/pane.deb" | sha256sum -c - \
    && apt-get install -y /tmp/pane.deb \
    && npm install -g "npm@${PANE_NPM_VERSION}" \
    && npm install -g "runpane@${PANE_VERSION}" "@openai/codex@${PANE_CODEX_CLI_VERSION}" \
    && rm -f /tmp/pane.deb \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /runtime/pane /runtime/repos /runtime/ssh /runtime/tmp \
    && chown -R soundatlas:soundatlas /runtime

COPY frontend/package.json frontend/package-lock.json /tmp/playwright/

RUN cd /tmp/playwright \
    && npm ci --ignore-scripts \
    && PLAYWRIGHT_BROWSERS_PATH=/opt/soundatlas-playwright-browsers npx playwright install chromium \
    && chown -R soundatlas:soundatlas /opt/soundatlas-playwright-browsers \
    && rm -rf /tmp/playwright /root/.npm

ENV TMPDIR=/runtime/tmp

USER soundatlas
WORKDIR /runtime/repos

ENTRYPOINT ["bash", "/runtime-config/pane-entrypoint.sh"]
CMD ["sleep", "infinity"]
