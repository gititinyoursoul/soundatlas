FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iptables libc-bin \
    && rm -rf /var/lib/apt/lists/*

COPY docker/pane-egress-guard.sh /usr/local/bin/pane-egress-guard
ENTRYPOINT ["sh", "/usr/local/bin/pane-egress-guard"]
