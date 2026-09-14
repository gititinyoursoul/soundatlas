FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends coreutils iptables libc-bin && rm -rf /var/lib/apt/lists/*
COPY bin/egress-guard.sh /usr/local/bin/pane-runtime-egress-guard
RUN chmod 0755 /usr/local/bin/pane-runtime-egress-guard
ENTRYPOINT ["/usr/local/bin/pane-runtime-egress-guard"]
