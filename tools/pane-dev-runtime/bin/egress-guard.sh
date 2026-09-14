#!/bin/sh
set -eu
umask 077

check_policy() {
  test -f /run/egress-ready
  iptables -w 5 -S OUTPUT > /run/egress-v4-current
  ip6tables -w 5 -S OUTPUT > /run/egress-v6-current
  cmp -s /run/egress-v4 /run/egress-v4-current
  cmp -s /run/egress-v6 /run/egress-v6-current
}
if [ "${1:-}" = check ]; then check_policy; exit 0; fi
test "$#" -eq 0
test "$(id -u)" -eq 0
rm -f /run/egress-ready
iptables -w 5 -P OUTPUT DROP; ip6tables -w 5 -P OUTPUT DROP
iptables -w 5 -F OUTPUT; ip6tables -w 5 -F OUTPUT
iptables -w 5 -A OUTPUT -o lo -j ACCEPT; ip6tables -w 5 -A OUTPUT -o lo -j ACCEPT
resolvers=$(awk '$1 == "nameserver" {print $2}' /etc/resolv.conf)
test -n "$resolvers"
for resolver in $resolvers; do test "$resolver" = 127.0.0.11; done
iptables -w 5 -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip6tables -w 5 -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
for range in 0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 192.0.0.0/24 192.0.2.0/24 192.168.0.0/16 198.18.0.0/15 198.51.100.0/24 203.0.113.0/24 224.0.0.0/4 240.0.0.0/4; do iptables -w 5 -A OUTPUT -d "$range" -j REJECT; done
ip6tables -w 5 -A OUTPUT ! -d 2000::/3 -j REJECT
for range in 2001::/23 2001:db8::/32 2002::/16 3fff::/20; do ip6tables -w 5 -A OUTPUT -d "$range" -j REJECT; done
iptables -w 5 -A OUTPUT -p tcp --dport 443 -j ACCEPT; ip6tables -w 5 -A OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -w 5 -S OUTPUT > /run/egress-v4; ip6tables -w 5 -S OUTPUT > /run/egress-v6
test "$(head -n 1 /run/egress-v4)" = '-P OUTPUT DROP'; test "$(head -n 1 /run/egress-v6)" = '-P OUTPUT DROP'
touch /run/egress-ready
check_policy
exec sleep infinity
