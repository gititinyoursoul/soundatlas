#!/bin/sh
set -eu
umask 077

# Snapshots live only in the companion's private tmpfs. Pane cannot write them.
check_policy() {
  test -f /run/egress-ready
  iptables -w 5 -S OUTPUT > /run/egress-v4-current
  ip6tables -w 5 -S OUTPUT > /run/egress-v6-current
  cmp -s /run/egress-v4 /run/egress-v4-current
  cmp -s /run/egress-v6 /run/egress-v6-current
}

if [ "${1:-}" = check ]; then
  check_policy
  exit
fi
test "$#" -eq 0
test "$(id -u)" -eq 0
rm -f /run/egress-ready

# Never flush an ACCEPT-policy chain, including during a manual rerun.
# Any failure is fatal; Compose must not start Pane until both families pass.
iptables -w 5 -P OUTPUT DROP
ip6tables -w 5 -P OUTPUT DROP
iptables -w 5 -F OUTPUT
ip6tables -w 5 -F OUTPUT
iptables -w 5 -A OUTPUT -o lo -j ACCEPT
ip6tables -w 5 -A OUTPUT -o lo -j ACCEPT

# Only Docker's embedded loopback resolver is supported. No broad port-53 rule.
resolvers=$(awk '$1 == "nameserver" {print $2}' /etc/resolv.conf)
test -n "$resolvers"
for resolver in $resolvers; do
  test "$resolver" = 127.0.0.11
done

destinations=${SOUNDATLAS_ALLOWED_OUTBOUND_DESTINATIONS-"backend:8000 frontend:5173"}
test -n "$destinations"
# Restrict configuration to the approved service/port pairs, including overrides.
for destination in $destinations; do
  case "$destination" in
    backend:8000|frontend:5173) ;;
    *) echo 'Unsupported Pane outbound destination' >&2; exit 1 ;;
  esac
done
test "$destinations" = 'backend:8000 frontend:5173'

iptables -w 5 -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip6tables -w 5 -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
for destination in $destinations; do
  host=${destination%:*}
  port=${destination##*:}
  # ahosts returns every usable family. getent failure must not be masked by a pipe.
  addresses=$(timeout 10 getent ahosts "$host")
  test -n "$addresses"
  ips=$(printf '%s\n' "$addresses" | awk '{print $1}' | sort -u)
  for ip in $ips; do
    case "$ip" in
      *:*) ip6tables -w 5 -A OUTPUT -p tcp -d "$ip" --dport "$port" -j ACCEPT ;;
      *) iptables -w 5 -A OUTPUT -p tcp -d "$ip" --dport "$port" -j ACCEPT ;;
    esac
  done
done

# Special-use destinations precede the public HTTPS exception.
for range in 0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 \
  169.254.0.0/16 172.16.0.0/12 192.0.0.0/24 192.0.2.0/24 \
  192.168.0.0/16 198.18.0.0/15 198.51.100.0/24 203.0.113.0/24 \
  224.0.0.0/4 240.0.0.0/4; do
  iptables -w 5 -A OUTPUT -d "$range" -j REJECT
done
# Permit only native global-unicast IPv6, excluding special-use subranges.
# This also excludes mapped IPv4, NAT64, ULA, link-local and multicast bypasses.
ip6tables -w 5 -A OUTPUT ! -d 2000::/3 -j REJECT
for range in 2001::/23 2001:db8::/32 2002::/16 3fff::/20; do
  ip6tables -w 5 -A OUTPUT -d "$range" -j REJECT
done
iptables -w 5 -A OUTPUT -p tcp --dport 443 -j ACCEPT
ip6tables -w 5 -A OUTPUT -p tcp --dport 443 -j ACCEPT

iptables -w 5 -S OUTPUT > /run/egress-v4
ip6tables -w 5 -S OUTPUT > /run/egress-v6
test "$(head -n 1 /run/egress-v4)" = '-P OUTPUT DROP'
test "$(head -n 1 /run/egress-v6)" = '-P OUTPUT DROP'
touch /run/egress-ready
check_policy
echo 'Pane egress ready (IPv4 and IPv6 default-drop)'
# No daemon, network listener, credentials, or workload runs in this container.
# Exiting never flushes rules. Recovery recreates the companion AND Pane.
exec sleep infinity
