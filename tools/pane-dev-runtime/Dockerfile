# syntax=docker/dockerfile:1
FROM node:24.11.1-bookworm-slim AS node
FROM debian:bookworm-slim

ARG PANE_VERSION=2.4.102
ARG PANE_SHA256=5e7155c9eb96aebbc575166ce26318c0475d2b26bf6df0dc5943c371deda594f
ARG CODEX_CLI_VERSION=0.154.0
ENV CODEX_HOME=/runtime/codex PANE_DIR=/runtime/pane PANE_REPOSITORY_ROOT=/runtime/repos PANE_SSH_DIR=/runtime/ssh TMPDIR=/runtime/tmp

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && apt-get update \
    && apt-get install -y --no-install-recommends bash bubblewrap ca-certificates curl git openssh-server \
      libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdbus-1-3 libdrm2 libexpat1 libfontconfig1 libgbm1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
    && curl -fsSLo /tmp/pane.deb "https://github.com/dcouple/Pane/releases/download/v${PANE_VERSION}/Pane-${PANE_VERSION}-linux-amd64.deb" \
    && echo "${PANE_SHA256}  /tmp/pane.deb" | sha256sum -c - \
    && apt-get install -y /tmp/pane.deb \
    && npm install -g "runpane@${PANE_VERSION}" "@openai/codex@${CODEX_CLI_VERSION}" \
    && rm -f /tmp/pane.deb \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 pane \
    && useradd --uid 10001 --gid pane --create-home --shell /bin/bash pane \
    && mkdir -p /runtime/pane /runtime/repos /runtime/ssh /runtime/codex /runtime/tmp /run/sshd \
    && chown -R pane:pane /runtime /run/sshd
COPY bin/runtime-entrypoint.sh /usr/local/bin/pane-runtime-entrypoint
COPY bin/runtime-status.sh /usr/local/bin/pane-runtime-status
COPY bin/attach-repository.sh /usr/local/bin/pane-runtime-attach-repository
COPY config/sshd_config /etc/pane-runtime/sshd_config
RUN chmod 0755 /usr/local/bin/pane-runtime-entrypoint /usr/local/bin/pane-runtime-status /usr/local/bin/pane-runtime-attach-repository
USER pane
WORKDIR /runtime/repos
ENTRYPOINT ["pane-runtime-entrypoint"]
CMD ["sleep", "infinity"]
