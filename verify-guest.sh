#!/usr/bin/env bash
# Verify the DVWA installation on the Ubuntu guest.
# Run as root: sudo bash verify-guest.sh
set -uo pipefail

pass=0
fail=0

check() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "[  PASS ] $name"
    pass=$((pass + 1))
  else
    echo "[  FAIL ] $name"
    fail=$((fail + 1))
  fi
}

check "Apache service active" systemctl is-active --quiet apache2
check "MariaDB service active" systemctl is-active --quiet mariadb
check "PHP installed" php --version
check "DVWA directory exists" test -d /var/www/html/DVWA
check "DVWA configuration exists" test -f /var/www/html/DVWA/config/config.inc.php
check "Local HTTP response" curl -fsS http://127.0.0.1/DVWA/
check "UFW active" ufw status

echo
echo "Passed: $pass"
echo "Failed: $fail"
[[ $fail -eq 0 ]]
