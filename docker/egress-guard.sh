#!/usr/bin/env sh
set -eu

APP_USER="${SOUNDATLAS_APP_USER:-soundatlas}"
WRITABLE_PATHS="${SOUNDATLAS_WRITABLE_PATHS:-}"
ALLOWED_OUTBOUND_PORTS="${SOUNDATLAS_ALLOWED_OUTBOUND_PORTS:-}"
ALLOWED_OUTBOUND_DESTINATIONS="${SOUNDATLAS_ALLOWED_OUTBOUND_DESTINATIONS:-}"

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
  iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
  iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

  if [ -n "$ALLOWED_OUTBOUND_PORTS" ]; then
    echo "port-only outbound exceptions are not supported; use SOUNDATLAS_ALLOWED_OUTBOUND_DESTINATIONS" >&2
    exit 1
  fi

  apply_allowed_destinations

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
    ip6tables -A OUTPUT -p udp --dport 53 -j ACCEPT
    ip6tables -A OUTPUT -p tcp --dport 53 -j ACCEPT

    ip6tables -A OUTPUT -d fe80::/10 -j REJECT
    ip6tables -A OUTPUT -d fc00::/7 -j REJECT
    ip6tables -A OUTPUT -d ff00::/8 -j REJECT

    ip6tables -A OUTPUT -p tcp --dport 443 -j ACCEPT
  fi
}

apply_allowed_destinations() {
  for destination in $ALLOWED_OUTBOUND_DESTINATIONS; do
    case "$destination" in
      *:*)
        host=${destination%:*}
        port=${destination##*:}
        ;;
      *)
        echo "Invalid outbound destination '$destination'; expected HOST:PORT" >&2
        exit 1
        ;;
    esac

    case "$host" in
      ""|*[!A-Za-z0-9.-]*)
        echo "Invalid outbound destination host '$host'" >&2
        exit 1
        ;;
    esac

    case "$port" in
      ""|*[!0-9]*)
        echo "Invalid outbound destination port '$port'" >&2
        exit 1
        ;;
    esac

    resolved_ips=$(getent ahostsv4 "$host" | awk '{print $1}' | sort -u)
    if [ -z "$resolved_ips" ]; then
      echo "Could not resolve outbound destination '$host'" >&2
      exit 1
    fi

    for ip in $resolved_ips; do
      iptables -A OUTPUT -p tcp -d "$ip" --dport "$port" -j ACCEPT
    done
  done
}

if [ "$(id -u)" = "0" ]; then
  prepare_writable_paths
  apply_egress_policy
  exec gosu "$APP_USER" "$@"
fi

exec "$@"
