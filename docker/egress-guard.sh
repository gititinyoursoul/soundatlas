#!/usr/bin/env sh
set -eu

APP_USER="${SOUNDATLAS_APP_USER:-soundatlas}"
WRITABLE_PATHS="${SOUNDATLAS_WRITABLE_PATHS:-}"
ALLOWED_INBOUND_PORTS="${SOUNDATLAS_ALLOWED_INBOUND_PORTS:-}"

prepare_writable_paths() {
  for path in $WRITABLE_PATHS; do
    mkdir -p "$path"
    chown -R "$APP_USER:$APP_USER" "$path"
  done
}

apply_egress_policy() {
  if [ "${SOUNDATLAS_EGRESS_GUARD:-enabled}" != "enabled" ]; then
    return
  fi

  if ! command -v iptables >/dev/null 2>&1; then
    echo "egress guard requested, but iptables is unavailable" >&2
    exit 1
  fi

  iptables -F OUTPUT
  iptables -P OUTPUT DROP

  iptables -A OUTPUT -o lo -j ACCEPT
  iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  iptables -A OUTPUT -p udp -d 127.0.0.11 --dport 53 -j ACCEPT
  iptables -A OUTPUT -p tcp -d 127.0.0.11 --dport 53 -j ACCEPT

  for port in $ALLOWED_INBOUND_PORTS; do
    iptables -A OUTPUT -p tcp --sport "$port" -j ACCEPT
  done

  iptables -A OUTPUT -d 0.0.0.0/8 -j REJECT
  iptables -A OUTPUT -d 10.0.0.0/8 -j REJECT
  iptables -A OUTPUT -d 100.64.0.0/10 -j REJECT
  iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT
  iptables -A OUTPUT -d 172.16.0.0/12 -j REJECT
  iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT
  iptables -A OUTPUT -d 224.0.0.0/4 -j REJECT
  iptables -A OUTPUT -d 240.0.0.0/4 -j REJECT

  iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT

  if command -v ip6tables >/dev/null 2>&1 && ip6tables -L OUTPUT >/dev/null 2>&1; then
    ip6tables -F OUTPUT
    ip6tables -P OUTPUT DROP

    ip6tables -A OUTPUT -o lo -j ACCEPT
    ip6tables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    ip6tables -A OUTPUT -d ::1/128 -j ACCEPT

    for port in $ALLOWED_INBOUND_PORTS; do
      ip6tables -A OUTPUT -p tcp --sport "$port" -j ACCEPT
    done

    ip6tables -A OUTPUT -d fe80::/10 -j REJECT
    ip6tables -A OUTPUT -d fc00::/7 -j REJECT
    ip6tables -A OUTPUT -d ff00::/8 -j REJECT

    ip6tables -A OUTPUT -p tcp --dport 443 -j ACCEPT
  fi
}

if [ "$(id -u)" = "0" ]; then
  prepare_writable_paths
  apply_egress_policy
  exec gosu "$APP_USER" "$@"
fi

exec "$@"
