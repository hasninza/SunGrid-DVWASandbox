#!/bin/bash
set -eu -o pipefail
export LC_ALL=C
printf 'Guest: %s | ' "$(hostname)"
date -u '+%F %T UTC'
. /etc/os-release
echo "OS: $PRETTY_NAME"
echo "Service: $(systemctl is-active workshop)"
systemctl is-active --quiet workshop
echo "Application listener:"
ss -H -ltn 'sport = :5000' | awk '{print $4}'
test "$(ss -H -ltn 'sport = :5000' | awk '{print $4}')" = '127.0.0.1:5000'
curl --noproxy '*' -fsS http://127.0.0.1:5000/ | grep -q 'Workshop service desk'
http_status=$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:5000/)
test "$http_status" = 200
echo "GET http://127.0.0.1:5000/ -> HTTP $http_status"
echo 'UFW baseline:'
ufw status verbose
ufw status | grep -q 'Status: active'
ufw status verbose | grep -q 'deny (incoming)'
ufw status | grep -E '5000/tcp on lo[[:space:]]+ALLOW' >/dev/null
if ufw status | awk '/ALLOW/ && !/5000\/tcp on lo / {print; bad=1}; END{exit bad}'; then :; else exit 1; fi
echo 'Guest interfaces:'
ip -br -4 addr
test -z "$(ip -4 route show default)"
test -z "$(ip -6 route show default)"
echo 'IPv4 and IPv6 default routes: none'
echo 'Isolated functional test with temporary records:'
PYTHONPATH=/opt/workshop/vendor python3 /opt/workshop/tests/check_roles.py
